from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    file_path: Path
    filename: str


class IngestRequest(BaseModel):
    file_path: Optional[Path] = Field(None, description="Path of previously uploaded file")
    url: Optional[str] = Field(None, description="URL to ingest")
    metadata: Dict[str, str] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    job_id: str


class JobStatusPayload(BaseModel):
    job_id: str
    kind: str
    source: str
    state: str
    created_at: str
    updated_at: str
    processed_chunks: int
    total_chunks: Optional[int] = None
    last_message: Optional[str] = None
    errors: List[str]


class JobStatusCollection(BaseModel):
    jobs: List[JobStatusPayload]


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    offset: int = 0
    filters: Optional[Dict[str, str]] = None


class SearchMatch(BaseModel):
    id: str
    score: float
    text: str
    metadata: Dict[str, str]


class SearchResponse(BaseModel):
    matches: list[SearchMatch]


