import asyncio
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from ...config import get_settings
from .base import VectorDB, VectorRecord


class QdrantVectorDB(VectorDB):
    def __init__(self):
        settings = get_settings()
        if not settings.qdrant_url:
            raise ValueError("Qdrant URL is required.")
        self.collection = settings.vectordb_collection
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self._vector_size: Optional[int] = None

    async def upsert(self, records: List[VectorRecord]) -> None:
        if not records:
            return
        if self._vector_size is None:
            self._vector_size = len(records[0]["embedding"])
            await asyncio.to_thread(self._ensure_collection)

        points = [
            qmodels.PointStruct(id=record["id"], vector=record["embedding"], payload=record["metadata"])
            for record in records
        ]
        await asyncio.to_thread(
            self.client.upsert,
            collection_name=self.collection,
            points=points,
        )

    async def query(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        result = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
            filter=self._build_filter(filters),
        )
        return [
            {
                "id": point.id,
                "score": point.score,
                "metadata": point.payload or {},
                "text": (point.payload or {}).get("text", ""),
            }
            for point in result
        ]

    async def delete(self, ids: List[str]) -> None:
        if not ids:
            return
        await asyncio.to_thread(
            self.client.delete,
            collection_name=self.collection,
            points_selector=qmodels.PointIdsList(points=ids),
        )

    def _ensure_collection(self) -> None:
        assert self._vector_size is not None
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(size=self._vector_size, distance=qmodels.Distance.COSINE),
            )

    def _build_filter(self, filters: Optional[Dict[str, Any]]):
        if not filters:
            return None
        must = []
        for key, value in filters.items():
            must.append(qmodels.FieldCondition(key=key, match=qmodels.MatchValue(value=value)))
        return qmodels.Filter(must=must)

