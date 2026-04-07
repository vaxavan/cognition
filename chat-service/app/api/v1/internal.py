from fastapi import APIRouter
router = APIRouter()
@router.post("/webhooks")
async def receive_webhook():
    return {"status": "ok", "message": "Webhook received"}
