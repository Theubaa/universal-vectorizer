from ...config import get_settings
from .base import VectorDB
from .chroma_db import ChromaVectorDB
from .pinecone_db import PineconeVectorDB
from .qdrant_db import QdrantVectorDB


def get_vectordb() -> VectorDB:
    settings = get_settings()
    provider = settings.vectordb_provider.lower()
    if provider == "chroma":
        return ChromaVectorDB()
    if provider == "pinecone":
        return PineconeVectorDB()
    if provider == "qdrant":
        return QdrantVectorDB()
    raise ValueError(f"Vector DB provider {settings.vectordb_provider} not supported.")


