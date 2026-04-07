import logging
from io import BytesIO

try:
    from PyPDF2 import PdfReader, PdfReadError

    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    PdfReadError = Exception  # Заглушка для except

logger = logging.getLogger(__name__)


class PDFParser:
    """
    Парсер PDF-файлов с фоллбэком на текст.

    Если контент не является валидным PDF (например, мок-данные для тестов),
    возвращает контент как есть, чтобы не ломать пайплайн.
    """

    def parse(self, content: bytes) -> str:
        """
        Извлекает текст из PDF или возвращает контент как текст.

        Args:
            content: Бинарные данные файла

        Returns:
            Извлечённый текст или исходный контент как строка
        """
        # Если библиотека не установлена — возвращаем как есть
        if not HAS_PYPDF2:
            logger.warning("⚠️ PyPDF2 не установлен, возвращаю контент как текст")
            return content.decode("utf-8", errors="replace")

        try:
            # Проверяем, начинается ли файл с сигнатуры PDF
            if not content.startswith(b"%PDF-"):
                logger.info(f"⚠️ Контент не похож на PDF (нет сигнатуры), возвращаю как текст")
                return content.decode("utf-8", errors="replace")

            # Пытаемся распарсить как настоящий PDF
            pdf_file = BytesIO(content)
            reader = PdfReader(pdf_file)

            texts = []
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    texts.append(f"[Страница {page_num}]\n{page_text.strip()}")

            result = "\n\n".join(texts)
            if result.strip():
                logger.info(f"📄 PDF распаршен: {len(result)} символов, {len(reader.pages)} страниц")
                return result
            else:
                # PDF есть, но текст не извлёкся (скан/картинки)
                logger.warning("⚠️ PDF не содержит извлекаемого текста, возвращаю метаданные")
                return f"[PDF: {len(reader.pages)} страниц, текст не извлечён]"

        except PdfReadError as e:
            # PyPDF2 не может прочитать файл как PDF
            logger.warning(f"⚠️ Ошибка чтения PDF: {e}. Возвращаю контент как текст.")
            return content.decode("utf-8", errors="replace")

        except Exception as e:
            # Любая другая ошибка — фоллбэк на текст
            logger.warning(f"⚠️ Неожиданная ошибка при парсинге PDF: {type(e).__name__}: {e}. Возвращаю как текст.")
            return content.decode("utf-8", errors="replace")