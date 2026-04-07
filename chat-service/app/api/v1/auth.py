from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
router = APIRouter()

@router.get("/me")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    return {"status": "auth_placeholder", "message": "Реализуй AuthService для полной аутентификации"}
