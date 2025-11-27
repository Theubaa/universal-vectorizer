from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, WebSocket, WebSocketDisconnect

from ..config import get_settings
from ..services.ingestion_service import ingestion_service
from ..services.search_service import search_service
from .schemas import (
    IngestRequest,
    IngestResponse,
    JobStatusCollection,
    JobStatusPayload,
    SearchRequest,
    SearchResponse,
    UploadResponse,
)

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile):
    path = await ingestion_service.upload(file)
    return UploadResponse(file_path=path, filename=file.filename or Path(path).name)


@router.post("/ingest", response_model=IngestResponse)
async def ingest(payload: IngestRequest):
    if not payload.file_path and not payload.url:
        raise HTTPException(status_code=400, detail="Either file_path or url must be provided.")

    if payload.file_path:
        path = Path(payload.file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found.")
        job_id = await ingestion_service.ingest_file(path, payload.metadata)
    else:
        job_id = await ingestion_service.ingest_url(payload.url, payload.metadata)

    return IngestResponse(job_id=job_id)


@router.get("/ingest/jobs", response_model=JobStatusCollection)
async def list_jobs():
    jobs = [status.to_dict() for status in ingestion_service.list_jobs()]
    return JobStatusCollection(jobs=jobs)


@router.get("/ingest/{job_id}/status", response_model=JobStatusPayload)
async def job_status(job_id: str):
    status = ingestion_service.get_job(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JobStatusPayload(**status.to_dict())


@router.websocket("/ws/ingest/{job_id}")
async def job_stream(websocket: WebSocket, job_id: str):
    if not settings.enable_websockets:
        await websocket.close()
        return
    await websocket.accept()
    queue = ingestion_service.subscribe(job_id)
    try:
        while True:
            update = await queue.get()
            await websocket.send_json(update)
    except WebSocketDisconnect:
        pass
    finally:
        ingestion_service.unsubscribe(job_id, queue)


@router.post("/search", response_model=SearchResponse)
async def search(payload: SearchRequest):
    matches = await search_service.search(payload.query, payload.top_k, payload.offset, payload.filters)
    return SearchResponse(matches=matches)


