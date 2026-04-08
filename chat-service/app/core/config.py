from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Chat Service"
    DEBUG: bool = True

    # === База данных ===
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat.db"

    # === MinIO / S3 ===
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_BUCKET: str = "uploads"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"

    # === Внешние сервисы ===
    CONTEXT_ENGINE_URL: str = "http://localhost:8002"

    # === Безопасность ===
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # === SMTP ===
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # ← вместо ignore

settings = Settings()