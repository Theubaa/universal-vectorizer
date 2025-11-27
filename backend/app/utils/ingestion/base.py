from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Protocol


@dataclass
class StreamedDocument:
    chunks: Iterable[str]
    metadata: Dict[str, str]


class IngestionHandler(ABC):
    supported_types: List[str] = []

    @abstractmethod
    def stream(self, source: Path) -> StreamedDocument:
        """Return an iterable of text chunks plus metadata without loading entire file."""


class PluginFactory(Protocol):
    def __call__(self, *args, **kwargs) -> IngestionHandler:
        ...


