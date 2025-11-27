import asyncio
from typing import List

from sentence_transformers import SentenceTransformer

from ...config import get_settings
from .base import EmbeddingBackend, EmbeddingResult


class HuggingFaceBackend(EmbeddingBackend):
    def __init__(self):
        settings = get_settings()
        self.model_name = settings.hf_model_name
        self.model = SentenceTransformer(self.model_name)

    async def embed(self, texts: List[str]) -> List[EmbeddingResult]:
        def _encode():
            return self.model.encode(texts, convert_to_numpy=False, show_progress_bar=False)

        vectors = await asyncio.to_thread(_encode)
        return [EmbeddingResult(vector=list(vec), model=self.model_name) for vec in vectors]


