from pydantic import BaseModel
from typing import Optional
class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)
class ChatResponse(BaseModel):
    id: int
    last_message: Optional[str] = None
    class Config: from_attributes = True
