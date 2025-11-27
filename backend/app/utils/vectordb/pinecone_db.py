import asyncio
from typing import Any, Dict, List, Optional

from pinecone import Pinecone

from ...config import get_settings
from .base import VectorDB, VectorRecord


class PineconeVectorDB(VectorDB):
    def __init__(self):
        settings = get_settings()
        if not settings.pinecone_api_key or not settings.pinecone_index:
            raise ValueError("Pinecone credentials and index name are required.")
        self.namespace = settings.vectordb_collection
        self.client = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.client.Index(settings.pinecone_index)

    async def upsert(self, records: List[VectorRecord]) -> None:
        if not records:
            return
        vectors = [
            {"id": record["id"], "values": record["embedding"], "metadata": record["metadata"]}
            for record in records
        ]
        await asyncio.to_thread(
            self.index.upsert,
            vectors=vectors,
            namespace=self.namespace,
        )

    async def query(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        result = await asyncio.to_thread(
            self.index.query,
            vector=query_embedding,
            namespace=self.namespace,
            top_k=top_k,
            include_metadata=True,
            include_values=False,
            filter=filters,
        )
        return [
            {
                "id": match["id"],
                "score": match["score"],
                "metadata": match.get("metadata", {}),
                "text": match.get("metadata", {}).get("text", ""),
            }
            for match in result.get("matches", [])
        ]

    async def delete(self, ids: List[str]) -> None:
        if not ids:
            return
        await asyncio.to_thread(
            self.index.delete,
            ids=ids,
            namespace=self.namespace,
        )

