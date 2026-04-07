def chunk_text(text: str, max_size: int = 500, overlap: int = 50):
    """Разбивает текст на перекрывающиеся чанки"""
    if not text or not text.strip():
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "text": chunk,
                "page": None,
                "meta": {"start": start, "end": end}
            })

        # Сдвиг с overlap
        if len(chunk) > overlap:
            start = end - overlap
        else:
            break

    return chunks
