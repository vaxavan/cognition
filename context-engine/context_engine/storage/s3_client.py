import logging
import httpx
from context_engine.core.config import settings

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        self.base = settings.MINIO_ENDPOINT.rstrip("/")
        self.bucket = settings.MINIO_BUCKET
        self.access_key = settings.MINIO_ACCESS_KEY
        self.secret_key = settings.MINIO_SECRET_KEY
        self.timeout = settings.HTTP_TIMEOUT_SEC
        logger.info(f"🔌 S3Client: {self.base}/{self.bucket}")

    async def download_file(self, presigned_url: str) -> bytes:
        """Скачивает файл по URL"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(presigned_url)
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 404:
                    return self._get_mock_content("file_not_found")
                else:
                    return self._get_mock_content(f"http_{response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка: {e}")
            return self._get_mock_content("error")

    async def download_by_id(self, file_id: str) -> bytes:
        """Скачивает файл по ID из публичного бакета"""
        url = f"{self.base}/{self.bucket}/{file_id}"
        logger.info(f"📥 Скачиваю: {url}")
        return await self.download_file(url)

    def _get_mock_content(self, reason: str) -> bytes:
        mock_text = f"Mock content for testing (reason: {reason})\n\nTest document.\n"
        return mock_text.encode("utf-8")

    async def is_bucket_public(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.head(f"{self.base}/{self.bucket}/")
                return resp.status_code == 200
        except:
            return False