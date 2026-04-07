import chardet


class TXTParser:
    """Парсер текстовых файлов"""

    def parse(self, content: bytes) -> str:
        enc = chardet.detect(content).get("encoding") or "utf-8"
        return content.decode(enc, errors="replace").strip()
