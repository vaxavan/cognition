import uuid
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.schemas.file import FileUploadRequest, FileResponse
from app.repositories.file_repo import FileRepository
from app.models.file import FileStatus
from datetime import timedelta
from minio import Minio
from sqlalchemy import select
from app.models.file import File


logger = logging.getLogger(__name__)


class FileService:
    def __init__(self, db_session: AsyncSession):
        self.repo = FileRepository(db_session)
        self.context_url = settings.CONTEXT_ENGINE_URL.rstrip("/")
        self.http_timeout = 30.0

    async def generate_presigned_url(self, req: FileUploadRequest) -> FileResponse:
        """Генерирует presigned URL и создаёт запись в БД"""
        file_id = str(uuid.uuid4())

        # 1. Создаём запись в БД
        file_record = await self.repo.create(req, file_id)
        logger.info(f"🗄️ Запись создана: file_id={file_id}, filename={req.filename}")

        # 2. Генерируем настоящий presigned URL через MinIO
        minio_client = Minio(
            settings.MINIO_ENDPOINT.replace("http://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        
        upload_url = minio_client.presigned_put_object(
            settings.MINIO_BUCKET,
            file_id,
            expires=timedelta(hours=1)
        )

        return FileResponse(
            file_id=file_record.file_id,
            upload_url=upload_url,
            status=file_record.status.value,
            context_id=file_record.context_id
        )
    
    async def confirm_upload(self, req: FileUploadRequest) -> FileResponse:
        logger.info(f"🔄 confirm_upload: file_id={req.file_id}, filename={req.filename}")

        # 1. Ищем запись по file_id
        file_record = None
        if req.file_id:
            file_record = await self.repo.get_by_file_id(req.file_id)
        
        if not file_record:
            logger.error(f"❌ Запись не найдена: file_id={req.file_id}")
            return FileResponse(file_id=req.file_id or "unknown", status="error", context_id=None)

        file_id = file_record.file_id

        # 2. Вызываем Context Engine
        try:
            logger.info(f"🌐 Вызываю context-engine: {self.context_url}/internal/process")
            context_response = await self._call_context_engine(file_id, req.filename)
            logger.info(f"✅ context-engine: chunks={len(context_response.get('chunks', []))}")
            
            context_id = context_response.get("context_id", f"ctx_{file_id}")
            await self._update_file_status(file_record, FileStatus.ready, context_id)
            
            return FileResponse(
                file_id=file_id,
                status=FileStatus.ready.value,
                context_id=context_id
            )
        except Exception as e:
            logger.error(f"❌ Context Engine error: {e}")
            await self._update_file_status(file_record, FileStatus.error, None)
            return FileResponse(
                file_id=file_id,
                status=FileStatus.error.value,
                context_id=None
            )
    
    async def _call_context_engine(self, file_id: str, filename: str) -> dict:
        """Вызывает context-engine через HTTP"""
        url = f"{self.context_url}/internal/process"
        payload = {
            "file_id": file_id,
            "filename": filename,
            "read_url": None
        }

        logger.debug(f"🌐 POST {url} with payload: {payload}")

        async with httpx.AsyncClient(timeout=self.http_timeout) as client:
            response = await client.post(url, json=payload)
            logger.debug(f"📡 Ответ: {response.status_code} - {response.text[:200] if response.text else 'empty'}")

            if response.status_code == 200:
                return response.json()
            else:
                raise httpx.HTTPStatusError(
                    f"Unexpected status {response.status_code}",
                    request=response.request,
                    response=response
                )

    async def _update_file_status(self, file_record, new_status: FileStatus, context_id: str | None):
        """
        Обновляет статус файла с явным коммитом.
        """
        try:
            file_record.status = new_status
            if context_id:
                file_record.context_id = context_id

            await self.repo.session.commit()
            await self.repo.session.refresh(file_record)
            logger.debug(f"💾 БД обновлена: status={new_status.value}, context_id={context_id}")

        except Exception as e:
            logger.error(f"❌ Ошибка обновления БД: {e}")
            await self.repo.session.rollback()
            raise