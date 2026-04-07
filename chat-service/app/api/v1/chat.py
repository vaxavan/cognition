from fastapi import APIRouter
router = APIRouter()
@router.post("/")
async def create_chat():
    return {"status": "chat_placeholder", "message": "Реализуй ChatService для полноценного чата"}
