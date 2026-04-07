from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from context_engine.core.config import settings
from context_engine.api.v1.routers.process import router as process_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager"""
    print(f"🚀 {settings.APP_NAME} v{__import__('context_engine').__version__} запускается...")
    yield
    print("🛑 Контекст-движок остановлен")


def create_application() -> FastAPI:
    """Factory: создаёт FastAPI приложение"""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # CORS для разработки
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Роутеры
    app.include_router(process_router, prefix="/internal", tags=["processing"])

    # Health checks
    @app.get("/", tags=["health"])
    def root():
        return {
            "service": "context-engine",
            "status": "running",
            "version": __import__('context_engine').__version__
        }

    @app.get("/health", tags=["health"])
    def health():
        return {"status": "healthy"}

    @app.get("/ready", tags=["health"])
    def ready():
        return {"status": "ready"}

    return app


app = create_application()
