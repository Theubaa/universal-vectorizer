from typing import List

from openai import AsyncOpenAI

from ...config import get_settings
from .base import EmbeddingBackend, EmbeddingResult


class OpenAIBackend(EmbeddingBackend):
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing.")
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def embed(self, texts: List[str]) -> List[EmbeddingResult]:
        response = await self.client.embeddings.create(
            input=texts,
            model=self.settings.openai_model,
        )
        return [
            EmbeddingResult(vector=data.embedding, model=self.settings.openai_model)
            for data in response.data
        ]


