from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JobStatus:
    job_id: str
    kind: str
    source: str
    state: str = "pending"
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    processed_chunks: int = 0
    total_chunks: Optional[int] = None
    last_message: Optional[str] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload


class IngestionJobManager:
    """Tracks ingestion jobs, provides status snapshots + websocket updates."""

    def __init__(self):
        self._jobs: Dict[str, JobStatus] = {}
        self._watchers: Dict[str, List[asyncio.Queue]] = {}

    def create_job(self, job_id: str, kind: str, source: str) -> JobStatus:
        status = JobStatus(job_id=job_id, kind=kind, source=source)
        self._jobs[job_id] = status
        self._notify(job_id)
        return status

    def update(self, job_id: str, **fields) -> JobStatus:
        status = self._jobs[job_id]
        for key, value in fields.items():
            setattr(status, key, value)
        status.updated_at = _now()
        self._notify(job_id)
        return status

    def increment_chunks(self, job_id: str, count: int) -> JobStatus:
        status = self._jobs[job_id]
        status.processed_chunks += count
        status.updated_at = _now()
        self._notify(job_id)
        return status

    def fail(self, job_id: str, error: str) -> JobStatus:
        status = self._jobs[job_id]
        status.state = "failed"
        status.errors.append(error)
        status.last_message = error
        status.updated_at = _now()
        self._notify(job_id)
        return status

    def succeed(self, job_id: str, message: Optional[str] = None) -> JobStatus:
        status = self._jobs[job_id]
        status.state = "completed"
        status.last_message = message
        status.updated_at = _now()
        self._notify(job_id)
        return status

    def get(self, job_id: str) -> Optional[JobStatus]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> List[JobStatus]:
        return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def subscribe(self, job_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._watchers.setdefault(job_id, []).append(queue)
        # send immediate snapshot
        if job_id in self._jobs:
            queue.put_nowait(self._jobs[job_id].to_dict())
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        if job_id not in self._watchers:
            return
        self._watchers[job_id] = [q for q in self._watchers[job_id] if q is not queue]
        if not self._watchers[job_id]:
            self._watchers.pop(job_id)

    def _notify(self, job_id: str) -> None:
        status = self._jobs.get(job_id)
        if not status:
            return
        payload = status.to_dict()
        for queue in self._watchers.get(job_id, []):
            if queue.full():
                continue
            queue.put_nowait(payload)


