from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import SendCodeRequest, VerifyRequest, TokenResponse  # ← напрямую из файла
from app.api.v1.dependencies import get_db
from app.services import auth as auth_service
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-code")
async def send_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    auth_service.send_verification_code(request.email)
    return {"message": "Код отправлен"}

@router.post("/verify", response_model=TokenResponse)
async def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    if not auth_service.verify_code(request.email, request.code):
        raise HTTPException(status_code=400, detail="Неверный код")
    
    user = await auth_service.get_or_create_user(db, request.email, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверный пароль")
    
    token = create_access_token({"sub": user.email, "user_id": user.id})
    return TokenResponse(access_token=token)