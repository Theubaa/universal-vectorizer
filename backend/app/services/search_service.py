from typing import Dict, List, Optional

from ..utils.embeddings.factory import get_embedding_backend
from ..utils.preprocess.cleaner import TextCleaner
from ..utils.vectordb.factory import get_vectordb


class SearchService:
    def __init__(self):
        self.embedder = get_embedding_backend()
        self.vector_db = get_vectordb()
        self.cleaner = TextCleaner()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        offset: int = 0,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[Dict]:
        text = self.cleaner.clean(query)
        embedding = (await self.embedder.embed([text]))[0]
        n_results = max(top_k + offset, top_k)
        matches = await self.vector_db.query(embedding.vector, top_k=n_results, filters=filters)
        return matches[offset:offset + top_k]


search_service = SearchService()


