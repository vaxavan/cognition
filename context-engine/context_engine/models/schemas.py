from enum import StrEnum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProcessingStatus(StrEnum):
    """Статусы обработки"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Chunk(BaseModel):
    """Текстовый чанк"""
    text: str = Field(..., min_length=1, max_length=2000, description="Текст чанка")
    page: Optional[int] = Field(None, ge=1, description="Номер страницы")
    meta: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Метаданные")
    model_config = ConfigDict(from_attributes=True)


class ProcessRequest(BaseModel):
    """Запрос на обработку"""
    file_id: str = Field(..., min_length=1, max_length=255, description="ID файла")
    filename: Optional[str] = Field(None, description="Имя файла")
    read_url: Optional[str] = Field(None, description="Presigned URL для скачивания")


class ProcessResponse(BaseModel):
    """Ответ после обработки"""
    status: ProcessingStatus = Field(..., description="Статус")
    context_id: str = Field(..., description="ID контекста")
    chunks: List[Chunk] = Field(default_factory=list, description="Чанки")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные")
    model_config = ConfigDict(from_attributes=True)
