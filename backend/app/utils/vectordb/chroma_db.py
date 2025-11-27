import asyncio
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from ...config import get_settings
from .base import VectorDB, VectorRecord


class ChromaVectorDB(VectorDB):
    def __init__(self):
        settings = get_settings()
        self.collection = chromadb.PersistentClient(
            path=str(settings.vectordb_path),
            settings=ChromaSettings(anonymized_telemetry=False),
        ).get_or_create_collection(name=settings.vectordb_collection)

    async def upsert(self, records: List[VectorRecord]) -> None:
        if not records:
            return

        async def _write():
            self.collection.upsert(
                ids=[record["id"] for record in records],
                embeddings=[record["embedding"] for record in records],
                metadatas=[record["metadata"] for record in records],
                documents=[record["metadata"].get("text", "") for record in records],
            )

        await asyncio.to_thread(_write)

    async def query(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        def _query():
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filters,
            )

        result = await asyncio.to_thread(_query)
        matches = []
        for idx in range(len(result["ids"][0])):
            matches.append(
                {
                    "id": result["ids"][0][idx],
                    "score": result["distances"][0][idx],
                    "metadata": result["metadatas"][0][idx],
                    "text": result["documents"][0][idx],
                }
            )
        return matches

    async def delete(self, ids: List[str]) -> None:
        if not ids:
            return

        await asyncio.to_thread(lambda: self.collection.delete(ids=ids))


