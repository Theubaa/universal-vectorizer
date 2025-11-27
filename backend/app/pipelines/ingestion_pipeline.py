import asyncio
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from ..config import get_settings
from ..core.checkpoint import CheckpointStore
from ..core.progress import IngestionJobManager
from ..logger import logger
from ..utils.chunking.hybrid_chunker import Chunk, HybridChunker
from ..utils.embeddings.base import EmbeddingResult
from ..utils.embeddings.factory import get_embedding_backend, get_fallback_backend
from ..utils.ingestion.registry import registry
from ..utils.ingestion.url_handler import URLHandler
from ..utils.preprocess.cleaner import TextCleaner
from ..utils.vectordb.base import VectorRecord
from ..utils.vectordb.factory import get_vectordb


class StreamingIngestionPipeline:
    """End-to-end streaming ingestion with checkpoints + batched embeddings."""

    def __init__(self, job_manager: IngestionJobManager):
        self.settings = get_settings()
        self.chunker = HybridChunker(
            chunk_size=self.settings.default_chunk_size,
            chunk_overlap=self.settings.default_chunk_overlap,
        )
        self.cleaner = TextCleaner()
        self.embedder = get_embedding_backend()
        self.fallback_embedder = get_fallback_backend(self.settings.embedding_backend)
        self.vector_db = get_vectordb()
        self.job_manager = job_manager

    async def ingest_file(
        self,
        job_id: str,
        path: Path,
        extra_metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        handler = registry.resolve(path)
        streamed = handler.stream(path)
        metadata = {**streamed.metadata, **(extra_metadata or {})}
        text_stream = self.cleaner.clean_stream(streamed.chunks)
        await self._process_stream(job_id, text_stream, metadata)

    async def ingest_url(
        self,
        job_id: str,
        url: str,
        extra_metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        handler = URLHandler()
        streamed = handler.stream_from_url(url)
        metadata = {**streamed.metadata, **(extra_metadata or {})}
        text_stream = self.cleaner.clean_stream(streamed.chunks)
        await self._process_stream(job_id, text_stream, metadata)

    async def _process_stream(self, job_id: str, text_stream: Iterable[str], metadata: Dict[str, str]) -> None:
        checkpoint = CheckpointStore(job_id)
        snapshot = checkpoint.load()
        already_processed = snapshot.get("chunks_processed", 0)
        chunk_batch: List[Chunk] = []
        chunk_idx = 0
        processed_since_checkpoint = 0

        for chunk in self.chunker.iter_chunks(text_stream, metadata):
            if chunk_idx < already_processed:
                chunk_idx += 1
                continue

            chunk_batch.append(chunk)
            chunk_idx += 1
            if len(chunk_batch) >= self.settings.chunk_batch_size:
                await self._flush_batch(job_id, chunk_batch)
                processed_since_checkpoint += len(chunk_batch)
                chunk_batch = []
                self.job_manager.increment_chunks(job_id, processed_since_checkpoint)
                processed_since_checkpoint = 0
                checkpoint.write({"chunks_processed": chunk_idx})

        if chunk_batch:
            await self._flush_batch(job_id, chunk_batch)
            self.job_manager.increment_chunks(job_id, len(chunk_batch))
            checkpoint.write({"chunks_processed": chunk_idx})

        checkpoint.delete()
        logger.info("Job %s completed. Total chunks %s", job_id, chunk_idx)

    async def _flush_batch(self, job_id: str, chunks: List[Chunk]) -> None:
        embeddings = await self._embed_with_retry(job_id, chunks)
        vectors = self._to_vector_records(chunks, embeddings)
        await self.vector_db.upsert(vectors)

    async def _embed_with_retry(self, job_id: str, chunks: List[Chunk]) -> List[EmbeddingResult]:
        texts = [chunk.text for chunk in chunks]
        delay = 1.0
        last_error: Optional[str] = None
        for attempt in range(self.settings.embedding_max_retries):
            try:
                return await self.embedder.embed(texts)
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                logger.warning("Embedding attempt %s failed for job %s: %s", attempt + 1, job_id, exc)
                await asyncio.sleep(delay)
                delay *= self.settings.embedding_retry_backoff
        logger.error("Falling back to secondary embedder for job %s after error %s", job_id, last_error)
        return await self.fallback_embedder.embed(texts)

    def _to_vector_records(self, chunks: List[Chunk], embeddings: List[EmbeddingResult]) -> List[VectorRecord]:
        records: List[VectorRecord] = []
        for chunk, embedding in zip(chunks, embeddings):
            records.append(
                {
                    "id": chunk.id,
                    "embedding": embedding.vector,
                    "metadata": {
                        **chunk.metadata,
                        "text": chunk.text,
                        "embedding_model": embedding.model,
                    },
                }
            )
        return records


pipeline: Optional[StreamingIngestionPipeline] = None


def init_pipeline(manager: IngestionJobManager) -> StreamingIngestionPipeline:
    global pipeline
    pipeline = StreamingIngestionPipeline(job_manager=manager)
    return pipeline


