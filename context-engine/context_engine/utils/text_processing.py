import re


def normalize_whitespace(text: str) -> str:
    """Нормализует пробелы и переносы"""
    text = re.sub(r"[\t\r]+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return re.sub(r" +", " ", text).strip()
