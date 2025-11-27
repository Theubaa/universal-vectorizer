from pathlib import Path
from typing import Generator

import pdfplumber

from .base import IngestionHandler, StreamedDocument


class PDFHandler(IngestionHandler):
    supported_types = [".pdf"]

    def stream(self, source: Path) -> StreamedDocument:
        def iterator() -> Generator[str, None, None]:
            with pdfplumber.open(source) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    if text:
                        yield text

        return StreamedDocument(chunks=iterator(), metadata={"source": str(source), "type": "pdf"})


