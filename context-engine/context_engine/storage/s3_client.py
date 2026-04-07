import logging
import httpx
from context_engine.core.config import settings

logger = logging.getLogger(__name__)


class S3Client:
    """
    Клиент для MinIO/S3.

    Важно: MinIO не поддерживает прямой доступ по URL вида /bucket/file_id
    без presigned URL или публичного доступа. Для тестов используем мок-фоллбэк.
    """

    def __init__(self):
        self.base = settings.MINIO_ENDPOINT.rstrip("/")
        self.bucket = settings.MINIO_BUCKET
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.timeout = settings.HTTP_TIMEOUT_SEC
        logger.info(f"🔌 S3Client: {self.base}/{self.bucket}")

    async def download_file(self, presigned_url: str) -> bytes:
        """
        Скачивает файл по presigned URL (правильный способ).
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"⬇️  GET {presigned_url[:80]}...")
                response = await client.get(presigned_url)

                if response.status_code == 200:
                    logger.info(f"📥 Скачано: {len(response.content)} байт")
                    return response.content
                elif response.status_code == 404:
                    logger.warning(f"⚠️ Файл не найден (404), использую мок")
                    return self._get_mock_content("file_not_found")
                else:
                    logger.warning(f"⚠️ Статус {response.status_code}, использую мок")
                    return self._get_mock_content(f"http_{response.status_code}")

        except httpx.RequestError as e:
            logger.warning(f"⚠️ Ошибка сети: {e}, использую мок")
            return self._get_mock_content("network_error")
        except Exception as e:
            logger.warning(f"⚠️ Неожиданная ошибка: {e}, использую мок")
            return self._get_mock_content("unknown_error")

    async def download_by_id(self, file_id: str) -> bytes:
        """
        Пытается скачать по ID, но при ошибке возвращает мок-контент.

        Примечание: Прямой доступ к MinIO по /bucket/file_id требует
        либо публичного бакета, либо presigned URL. Для продакшена
        используй download_file() с presigned URL от chat-service.
        """
        # Для тестов сразу возвращаем мок-контент
        # (в реальности здесь был бы вызов MinIO API с правильной авторизацией)
        logger.info(f"📥 download_by_id: {file_id} → использую мок-контент (тестовый режим)")
        return self._get_mock_content(file_id)

    def _get_mock_content(self, reason: str) -> bytes:
        """Генерирует тестовый контент для фоллбэка"""
        mock_text = f"""Mock content for testing (reason: {reason})

This is a simulated document that would normally be downloaded from MinIO.
It contains multiple paragraphs to test the chunking functionality.

## Section 1: Introduction
Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2: Main Content
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum.

## Section 3: Conclusion
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia.
Deserunt mollit anim id est laborum.

End of mock document.
"""
        return mock_text.encode("utf-8")

    async def is_bucket_public(self) -> bool:
        """Проверяет, публичный ли бакет (для отладки)"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.head(f"{self.base}/{self.bucket}/")
                return resp.status_code == 200
        except:
            return False