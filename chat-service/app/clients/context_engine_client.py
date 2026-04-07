import httpx, logging
from app.core.config import settings
logger = logging.getLogger(__name__)

class ContextEngineClient:
    def __init__(self):
        self.base_url = settings.CONTEXT_ENGINE_URL
        self.timeout = httpx.Timeout(30.0)

    async def process_file(self, file_id: str, read_url: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/internal/process",
                    json={"file_id": file_id, "read_url": read_url},
                    headers={"X-Service": "chat-service"}
                )
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error(f"❌ Ошибка вызова context-engine: {e}")
                raise
