from pathlib import Path

from ..file_utils import stream_text_file
from .base import IngestionHandler, StreamedDocument


class TextHandler(IngestionHandler):
    supported_types = [".txt", ".md", ".html", ".log"]

    def stream(self, source: Path) -> StreamedDocument:
        return StreamedDocument(
            chunks=stream_text_file(source),
            metadata={"source": str(source), "type": "text"},
        )


