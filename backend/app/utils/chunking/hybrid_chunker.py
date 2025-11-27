from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict


class HybridChunker:
    """Streaming hybrid chunker (semantic pre-aggregation + fixed windows)."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def iter_chunks(self, text_stream: Iterable[str], metadata: dict) -> Iterator[Chunk]:
        buffer = ""
        chunk_idx = 0
        for block in text_stream:
            for unit in self._semantic_units(block):
                buffer = f"{buffer} {unit}".strip() if buffer else unit
                while len(buffer) >= self.chunk_size:
                    chunk_text = buffer[: self.chunk_size]
                    yield self._build_chunk(metadata, chunk_idx, chunk_text)
                    chunk_idx += 1
                    buffer = buffer[self.chunk_size - self.chunk_overlap :]
        if buffer:
            yield self._build_chunk(metadata, chunk_idx, buffer)

    def _semantic_units(self, text: str) -> Iterator[str]:
        paragraphs = (p.strip() for p in text.split("\n\n"))
        for paragraph in paragraphs:
            if not paragraph:
                continue
            sentences = paragraph.replace("\n", " ").split(". ")
            for sentence in sentences:
                stripped = sentence.strip()
                if stripped:
                    yield stripped

    def _build_chunk(self, metadata: dict, idx: int, text: str) -> Chunk:
        return Chunk(
            id=f"{metadata.get('source', 'unknown')}-chunk-{idx}",
            text=text,
            metadata={**metadata, "chunk_index": idx},
        )


