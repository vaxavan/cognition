from pathlib import Path
from context_engine.services.pdf_parser import PDFParser
from context_engine.services.docx_parser import DOCXParser
from context_engine.services.txt_parser import TXTParser


def get_parser(filename: str):
    """Factory: возвращает парсер по расширению"""
    ext = Path(filename).suffix.lower().lstrip(".")

    if ext == "pdf":
        return PDFParser()
    elif ext in ("docx", "doc"):
        return DOCXParser()
    else:
        return TXTParser()
