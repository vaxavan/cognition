from pydantic import BaseModel, Field, field_validator
from typing import Optional

class FileUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255, description="Имя файла")
    project_id: str = Field(..., min_length=1, description="ID проекта")
    sha256: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$", description="SHA256 хеш файла")

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        if not v.lower().endswith(('.pdf', '.docx', '.txt', '.md')):
            raise ValueError('Поддерживаются только: .pdf, .docx, .txt, .md')
        return v

class FileResponse(BaseModel):
    file_id: str
    upload_url: Optional[str] = None
    status: str
    context_id: Optional[str] = None

    class Config:
        from_attributes = True
