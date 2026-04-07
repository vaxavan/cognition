import logging
from fastapi import APIRouter, HTTPException, status
from context_engine.models.schemas import ProcessRequest, ProcessResponse, Chunk, ProcessingStatus
from context_engine.services.parser_factory import get_parser
from context_engine.services.chunker import chunk_text
from context_engine.storage.s3_client import S3Client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/process",
    response_model=ProcessResponse,
    status_code=status.HTTP_200_OK,
    summary="Обработать файл",
    description="Скачивает файл, парсит, чанкает и возвращает контекст"
)
async def process_file(req: ProcessRequest) -> ProcessResponse:
    """Основной эндпоинт обработки"""
    file_id = req.file_id
    logger.info(f"🔄 Обработка: file_id={file_id}")

    try:
        # Скачивание файла
        s3 = S3Client()
        if req.read_url:
            content = await s3.download_file(req.read_url)
            logger.info(f"📥 Скачано по URL: {len(content)} байт")
        else:
            content = await s3.download_by_id(file_id)
            logger.info(f"📥 Скачано по ID: {len(content)} байт")

        # Парсинг
        filename = req.filename or f"{file_id}.txt"
        parser = get_parser(filename)
        text = parser.parse(content)
        logger.info(f"📄 Распаршено: {len(text)} символов")

        # Чанкинг
        chunks_data = chunk_text(text)
        logger.info(f"✂️ Создано чанков: {len(chunks_data)}")

        # Ответ
        chunks = [
            Chunk(text=c["text"], page=c.get("page"), meta=c.get("meta"))
            for c in chunks_data
        ]

        return ProcessResponse(
            status=ProcessingStatus.READY,
            context_id=f"ctx_{file_id}",
            chunks=chunks,
            metadata={
                "source": filename,
                "total_chars": len(text),
                "chunks_count": len(chunks)
            }
        )

    except FileNotFoundError:
        logger.error(f"❌ Файл не найден: {file_id}")
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        logger.error(f"❌ Ошибка парсинга: {e}")
        raise HTTPException(status_code=422, detail=f"Parse error: {e}")
    except Exception as e:
        logger.exception(f"❌ Внутренняя ошибка: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
