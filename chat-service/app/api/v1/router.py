from fastapi import APIRouter
from app.api.v1 import auth, files, chat, internal

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(internal.router, prefix="/internal", tags=["internal"])
