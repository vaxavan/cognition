from fastapi import APIRouter

router = APIRouter()

@router.post("/process")
async def process_file(request: dict):
    return {"status": "ok", "file_id": request.get("file_id"), "chunks": []}