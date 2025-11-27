from pathlib import Path
from typing import Generator, List, Optional

import requests
from bs4 import BeautifulSoup

from .base import IngestionHandler, StreamedDocument


class URLHandler(IngestionHandler):
    supported_types = ["url"]

    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or "UniversalVectorizerBot/1.0"

    def stream(self, source: Path) -> StreamedDocument:
        raise NotImplementedError("Use stream_from_url for remote resources.")

    def stream_from_url(self, url: str) -> StreamedDocument:
        response = requests.get(
            url,
            headers={"User-Agent": self.user_agent},
            timeout=30,
            stream=True,
        )
        response.raise_for_status()
        chunks: List[str] = []
        for piece in response.iter_content(chunk_size=64 * 1024, decode_unicode=True):
            if piece:
                chunks.append(piece)
        html = "".join(chunks)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        def iterator() -> Generator[str, None, None]:
            for paragraph in text.split(". "):
                stripped = paragraph.strip()
                if stripped:
                    yield stripped

        metadata = {
            "source": url,
            "type": "url",
            "title": soup.title.string if soup.title else "",
        }
        return StreamedDocument(chunks=iterator(), metadata=metadata)


