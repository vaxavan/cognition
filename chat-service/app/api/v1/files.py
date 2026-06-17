from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.file_service import FileService
from app.schemas.file import FileUploadRequest, FileResponse
from fastapi import UploadFile, File
from minio import Minio
from app.core.config import settings
from app.api.v1.dependencies import get_db
from sqlalchemy import select
from app.models.file import File
import uuid
import logging


logger = logging.getLogger(__name__)



router = APIRouter()

@router.post("/request-upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def request_upload(req: FileUploadRequest, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Запрос presigned URL + создание записи в БД"""
    service = FileService(db)
    return await service.generate_presigned_url(req)

@router.post("/confirm-upload", response_model=FileResponse)
async def confirm_upload(req: FileUploadRequest, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """Подтверждение загрузки + обновление статуса в БД"""
    service = FileService(db)
    return await service.confirm_upload(req)


minio_client = Minio(
    settings.MINIO_ENDPOINT.replace("http://", ""),
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

@router.post("/upload")
async def upload_file_direct(file: UploadFile = File()):
    file_id = str(uuid.uuid4())
    minio_client.put_object(
        settings.MINIO_BUCKET,
        file_id,
        file.file,
        length=-1,
        part_size=10*1024*1024
    )
    return {"file_id": file_id, "filename": file.filename}

@router.get("/list")
async def list_files(db: AsyncSession = Depends(get_db)):
    """Список файлов с оригинальными именами из БД"""
    try:
        result = await db.execute(select(File).order_by(File.created_at.desc()))
        files = result.scalars().all()
        return {
            "files": [
                {"file_id": f.file_id, "filename": f.filename} 
                for f in files
            ]
        }
    except Exception as e:
        # Fallback — из MinIO (без имён)
        objects = minio_client.list_objects(settings.MINIO_BUCKET)
        return {
            "files": [
                {"file_id": obj.object_name, "filename": obj.object_name} 
                for obj in objects
            ]
        }
    

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: AsyncSession = Depends(get_db)):
    """Удаляет файл из MinIO и БД"""
    # Удалить из MinIO
    try:
        minio_client.remove_object(settings.MINIO_BUCKET, file_id)
    except Exception as e:
        logger.warning(f"MinIO delete error: {e}")
    
    # Удалить из БД
    result = await db.execute(select(File).where(File.file_id == file_id))
    file_record = result.scalar_one_or_none()
    if file_record:
        await db.delete(file_record)
        await db.commit()
        return {"status": "deleted", "file_id": file_id}
    
    return {"status": "not_found", "file_id": file_id}
