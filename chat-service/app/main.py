from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import setup_logger
from app.db.session import init_db, shutdown_db
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    await init_db()
    yield
    await shutdown_db()

def create_application() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)
    if settings.DEBUG:
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_application()
