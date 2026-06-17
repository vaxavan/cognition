import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import get_db
from app.schemas.chat import MessageCreate
from app.services.llm_client import DeepSeekYandexClient

router = APIRouter()
llm = DeepSeekYandexClient()

@router.post("/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    request: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    system_prompt = "Ты — полезный ассистент Cognition. Отвечай на русском языке."
    
    async def generate():
        async for chunk in llm.stream_text(system_prompt, request.content):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/")
async def create_chat():
    return {"id": "default", "name": "Чат"}