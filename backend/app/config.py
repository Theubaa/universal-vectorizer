from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Universal Vectorizer"
    environment: str = "development"
    allowed_origins: List[str] = ["*"]

    storage_dir: Path = Path("storage")
    temp_dir: Path = Path("storage") / "tmp"
    checkpoint_dir: Path = Path("storage") / "checkpoints"

    default_chunk_size: int = 800
    default_chunk_overlap: int = 200
    chunk_batch_size: int = 32
    embedding_batch_size: int = 64
    embedding_max_retries: int = 5
    embedding_retry_backoff: float = 1.8

    stream_read_size: int = 64 * 1024  # 64 KB
    max_upload_chunk_bytes: int = 4 * 1024 * 1024  # 4 MB

    openai_api_key: Optional[str] = None
    openai_model: str = "text-embedding-3-large"

    hf_model_name: str = "hkunlp/instructor-large"

    embedding_backend: str = "openai"  # openai | huggingface

    vectordb_provider: str = "chroma"
    vectordb_path: Path = Path("storage") / "chroma"
    vectordb_collection: str = "universal_vectorizer"
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index: Optional[str] = None
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None

    ingestion_checkpoint_interval: int = 5
    ingestion_concurrency: int = 2
    max_pending_jobs: int = 50

    enable_websockets: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    settings.vectordb_path.mkdir(parents=True, exist_ok=True)
    settings.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    return settings


