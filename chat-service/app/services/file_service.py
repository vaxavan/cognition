import uuid
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.schemas.file import FileUploadRequest, FileResponse
from app.repositories.file_repo import FileRepository
from app.models.file import FileStatus

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

        # 2. Генерируем presigned URL для MinIO
        upload_url = f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET}/{file_id}?presigned=1"

        return FileResponse(
            file_id=file_record.file_id,
            upload_url=upload_url,
            status=file_record.status.value,
            context_id=file_record.context_id
        )

    async def confirm_upload(self, req: FileUploadRequest) -> FileResponse:
        """
        Подтверждает загрузку:
        1. Находит запись в БД
        2. Вызывает context-engine для обработки
        3. Обновляет статус на 'ready'
        """
        logger.info(f"🔄 confirm_upload: filename={req.filename}, project={req.project_id}")

        # 1. Ищем запись в БД (по filename для теста)
        file_record = await self.repo.get_by_file_id(req.filename)

        if not file_record:
            logger.warning(f"⚠️ Файл не найден: {req.filename}, создаю новую запись")
            file_record = await self.repo.create(req, req.filename)

        file_id = file_record.file_id
        logger.info(f"📄 Обрабатываю: file_id={file_id}")

        # 2. Вызываем context-engine
        context_response = None
        try:
            logger.info(f"🌐 Вызываю context-engine: {self.context_url}/internal/process")
            context_response = await self._call_context_engine(file_id, req.filename)
            logger.info(
                f"✅ context-engine ответил: status={context_response.get('status')}, chunks={len(context_response.get('chunks', []))}")

        except httpx.ConnectError as e:
            logger.error(f"❌ Не удалось подключиться к context-engine: {e}")
            # Пробуем обновить статус на error с коммитом
            await self._update_file_status(file_record, FileStatus.error, None)
            return FileResponse(
                file_id=file_record.file_id,
                upload_url=None,
                status=FileStatus.error.value,
                context_id=None
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ context-engine вернул ошибку: {e.response.status_code} - {e.response.text[:200]}")
            await self._update_file_status(file_record, FileStatus.error, None)
            return FileResponse(
                file_id=file_record.file_id,
                upload_url=None,
                status=FileStatus.error.value,
                context_id=None
            )
        except Exception as e:
            logger.exception(f"❌ Неожиданная ошибка при вызове context-engine: {type(e).__name__}: {e}")
            await self._update_file_status(file_record, FileStatus.error, None)
            return FileResponse(
                file_id=file_record.file_id,
                upload_url=None,
                status=FileStatus.error.value,
                context_id=None
            )

        # 3. Если ответ получен — обновляем на ready
        if context_response and context_response.get("status") == "ready":
            context_id = context_response.get("context_id", f"ctx_{file_id}")
            await self._update_file_status(file_record, FileStatus.ready, context_id)
            logger.info(f"🗄️ Статус обновлён: file_id={file_id}, status=ready, context_id={context_id}")

            return FileResponse(
                file_id=file_record.file_id,
                upload_url=None,
                status=FileStatus.ready.value,
                context_id=context_id
            )
        else:
            # Ответ есть, но статус не ready
            logger.warning(
                f"⚠️ context-engine вернул статус: {context_response.get('status') if context_response else 'None'}")
            await self._update_file_status(file_record, FileStatus.error, None)
            return FileResponse(
                file_id=file_record.file_id,
                upload_url=None,
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
        Выносится в отдельный метод для надёжности.
        """
        try:
            file_record.status = new_status
            if context_id:
                file_record.context_id = context_id

            # Явный коммит
            await self.repo.session.commit()
            await self.repo.session.refresh(file_record)
            logger.debug(f"💾 БД обновлена: status={new_status.value}, context_id={context_id}")

        except Exception as e:
            logger.error(f"❌ Ошибка обновления БД: {e}")
            await self.repo.session.rollback()
            raise