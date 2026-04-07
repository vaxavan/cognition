# Добавь поле chunks в FileResponse
class FileResponse(BaseModel):
    file_id: str
    upload_url: Optional[str] = None
    status: str
    context_id: Optional[str] = None
    chunks: Optional[List[dict]] = None  # ← Добавь эту строку

    class Config:
        from_attributes = True