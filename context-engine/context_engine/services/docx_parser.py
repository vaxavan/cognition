import logging
from io import BytesIO

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

logger = logging.getLogger(__name__)


class DOCXParser:
    """Парсер DOCX"""

    def parse(self, content: bytes) -> str:
        if not HAS_DOCX:
            return "[python-docx not installed]"
        try:
            doc = Document(BytesIO(content))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            logger.error(f"DOCX parse error: {e}")
            raise ValueError(str(e))
