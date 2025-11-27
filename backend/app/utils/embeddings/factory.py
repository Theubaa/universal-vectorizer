from ...config import get_settings
from .base import EmbeddingBackend
from .hf_backend import HuggingFaceBackend
from .openai_backend import OpenAIBackend


def get_embedding_backend() -> EmbeddingBackend:
    settings = get_settings()
    if settings.embedding_backend == "huggingface":
        return HuggingFaceBackend()
    return OpenAIBackend()


def get_fallback_backend(primary: str) -> EmbeddingBackend:
    """Return an alternate backend if the primary one fails."""
    if primary == "huggingface":
        return OpenAIBackend()
    return HuggingFaceBackend()


