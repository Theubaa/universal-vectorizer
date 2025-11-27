from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Type

from .audio_handler import AudioHandler
from .base import IngestionHandler, PluginFactory
from .csv_handler import TabularHandler
from .image_handler import ImageHandler
from .json_handler import JSONHandler
from .pdf_handler import PDFHandler
from .text_handler import TextHandler


class IngestionRegistry:
    def __init__(self):
        self._handlers: Dict[str, PluginFactory] = {}
        self.register(TextHandler.supported_types, TextHandler)
        self.register(PDFHandler.supported_types, PDFHandler)
        self.register(ImageHandler.supported_types, ImageHandler)
        self.register(AudioHandler.supported_types, AudioHandler)
        self.register(TabularHandler.supported_types, TabularHandler)
        self.register(JSONHandler.supported_types, JSONHandler)

    def register(self, suffixes: List[str], handler_cls: Type[IngestionHandler]):
        for suffix in suffixes:
            self._handlers[suffix.lower()] = handler_cls

    def resolve(self, path: Path) -> IngestionHandler:
        suffix = path.suffix.lower()
        handler_cls = self._handlers.get(suffix)
        if not handler_cls:
            raise ValueError(f"No ingestion handler registered for suffix: {suffix}")
        return handler_cls()


registry = IngestionRegistry()


