from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class EmbeddingResult:
    vector: List[float]
    model: str


class EmbeddingBackend(ABC):
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[EmbeddingResult]:
        """Async embedding call with retry/backoff handled upstream."""


