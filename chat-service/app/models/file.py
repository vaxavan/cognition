from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.models.base import Base

class FileStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    error = "error"

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    project_id = Column(String, nullable=True, index=True)
    status = Column(Enum(FileStatus), default=FileStatus.pending, nullable=False)
    context_id = Column(String, nullable=True)
    sha256 = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<File(file_id='{self.file_id}', status='{self.status.value}')>"
