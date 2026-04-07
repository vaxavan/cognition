from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.file import File, FileStatus
from app.schemas.file import FileUploadRequest
from app.repositories.base import BaseRepository

class FileRepository(BaseRepository[File]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, File)

    async def create(self, req: FileUploadRequest, file_id: str) -> File:
        db_file = File(
            file_id=file_id,
            filename=req.filename,
            project_id=req.project_id,
            sha256=req.sha256,
            status=FileStatus.pending
        )
        self.session.add(db_file)
        await self.session.commit()
        await self.session.refresh(db_file)
        return db_file

    async def get_by_file_id(self, file_id: str) -> Optional[File]:
        stmt = select(File).where(File.file_id == file_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, file: File, status: FileStatus, context_id: Optional[str] = None) -> File:
        file.status = status
        if context_id:
            file.context_id = context_id
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def list_by_project(self, project_id: str, limit: int = 20, offset: int = 0) -> List[File]:
        stmt = select(File).where(File.project_id == project_id).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
