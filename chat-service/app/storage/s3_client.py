import logging
from minio import Minio
from minio.error import S3Error
from datetime import timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        # Убираем http:// из endpoint, т.к. minio-client ожидает просто host:port
        endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")

        self.client = Minio(
            endpoint,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False  # Для localhost без SSL
        )
        self.bucket = settings.MINIO_BUCKET

        logger.info("🔌 Подключение к MinIO инициализировано")
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"🪣 Бакет '{self.bucket}' создан")
        except S3Error as e:
            logger.error(f"❌ Ошибка создания бакета: {e}")
            raise

    def get_presigned_put_url(self, file_id: str, expires: int = 3600) -> str:
        try:
            url = self.client.presigned_put_object(
                self.bucket,
                file_id,
                expires=timedelta(seconds=expires)
            )
            logger.info(f"✅ Валидный presigned URL сгенерирован для {file_id}")
            return url
        except S3Error as e:
            logger.error(f"❌ Ошибка MinIO при генерации ссылки: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Не удалось подключиться к MinIO. Убедись, что он запущен: {e}")
            raise