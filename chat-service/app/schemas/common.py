from pydantic import BaseModel, Field
from typing import Optional

class ErrorResponse(BaseModel):
    detail: str

class Pagination(BaseModel):
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
