from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.file_service import FileService
from app.schemas.file import FileUploadRequest, FileResponse

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
