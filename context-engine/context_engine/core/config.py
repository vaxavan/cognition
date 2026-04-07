from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""

    APP_NAME: str = "Context Engine"
    DEBUG: bool = True

    # MinIO
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_BUCKET: str = "uploads"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"

    # Обработка
    DEFAULT_CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    HTTP_TIMEOUT_SEC: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
