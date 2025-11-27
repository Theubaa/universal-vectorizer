from pathlib import Path
from typing import Generator

import pytesseract
from PIL import Image

from .base import IngestionHandler, StreamedDocument


class ImageHandler(IngestionHandler):
    supported_types = [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]

    def stream(self, source: Path) -> StreamedDocument:
        def iterator() -> Generator[str, None, None]:
            image = Image.open(source)
            try:
                text = pytesseract.image_to_string(image)
                if text:
                    yield text
            finally:
                image.close()

        return StreamedDocument(chunks=iterator(), metadata={"source": str(source), "type": "image"})


