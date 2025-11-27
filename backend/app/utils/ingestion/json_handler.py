from pathlib import Path
from typing import Generator

import ijson

from .base import IngestionHandler, StreamedDocument


class JSONHandler(IngestionHandler):
    supported_types = [".json"]

    def stream(self, source: Path) -> StreamedDocument:
        def iterator() -> Generator[str, None, None]:
            with source.open("rb") as handle:
                parser = ijson.parse(handle)
                for prefix, event, value in parser:
                    if event in ("string", "number", "boolean"):
                        yield f"{prefix}: {value}"
                    elif event == "null":
                        yield f"{prefix}: null"

        return StreamedDocument(chunks=iterator(), metadata={"source": str(source), "type": "json"})


