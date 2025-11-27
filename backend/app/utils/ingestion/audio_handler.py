from pathlib import Path
from typing import Generator

import whisper

from .base import IngestionHandler, StreamedDocument


class AudioHandler(IngestionHandler):
    supported_types = [".mp3", ".wav", ".m4a", ".flac"]

    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)

    def stream(self, source: Path) -> StreamedDocument:
        def iterator() -> Generator[str, None, None]:
            result = self.model.transcribe(str(source))
            segments = result.get("segments") or []
            for segment in segments:
                text = segment.get("text")
                if text:
                    yield text.strip()
            # fallback if no segments
            if not segments and result.get("text"):
                yield result["text"]

        return StreamedDocument(chunks=iterator(), metadata={"source": str(source), "type": "audio"})


