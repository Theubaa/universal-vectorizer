import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import UploadFile

from ..config import get_settings
from ..core.progress import IngestionJobManager, JobStatus
from ..logger import logger
from ..pipelines.ingestion_pipeline import StreamingIngestionPipeline, init_pipeline
from ..utils.file_utils import save_upload_file


class IngestionService:
    def __init__(self):
        self.settings = get_settings()
        self.job_manager = IngestionJobManager()
        self.pipeline: StreamingIngestionPipeline = init_pipeline(self.job_manager)
        self._semaphore = asyncio.Semaphore(self.settings.ingestion_concurrency)

    async def upload(self, upload: UploadFile) -> Path:
        logger.info("Uploading file: %s", upload.filename)
        return await asyncio.to_thread(save_upload_file, upload)

    def list_jobs(self) -> List[JobStatus]:
        return self.job_manager.list_jobs()

    def get_job(self, job_id: str) -> Optional[JobStatus]:
        return self.job_manager.get(job_id)

    def subscribe(self, job_id: str) -> asyncio.Queue:
        return self.job_manager.subscribe(job_id)

    def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        self.job_manager.unsubscribe(job_id, queue)

    async def ingest_file(self, path: Path, metadata: Dict[str, str]) -> str:
        job_id = uuid.uuid4().hex
        self.job_manager.create_job(job_id, kind="file", source=str(path))
        asyncio.create_task(self._run_job(job_id, self.pipeline.ingest_file, path, metadata))
        return job_id

    async def ingest_url(self, url: str, metadata: Dict[str, str]) -> str:
        job_id = uuid.uuid4().hex
        self.job_manager.create_job(job_id, kind="url", source=url)
        asyncio.create_task(self._run_job(job_id, self.pipeline.ingest_url, url, metadata))
        return job_id

    async def _run_job(self, job_id: str, fn, *args, **kwargs) -> None:
        async with self._semaphore:
            self.job_manager.update(job_id, state="processing", last_message="Starting ingestion")
            try:
                await fn(job_id, *args, **kwargs)
                self.job_manager.succeed(job_id, message="Ingestion complete")
            except Exception as exc:  # noqa: BLE001
                logger.exception("Job %s failed", job_id)
                self.job_manager.fail(job_id, str(exc))


ingestion_service = IngestionService()


