from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class VectorRecord(Dict[str, Any]):
    id: str
    embedding: List[float]
    metadata: Dict[str, Any]


class VectorDB(ABC):
    @abstractmethod
    async def upsert(self, records: List[VectorRecord]) -> None:
        ...

    @abstractmethod
    async def query(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        ...


