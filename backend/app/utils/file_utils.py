import uuid
from pathlib import Path
from typing import Generator, Iterable

from fastapi import UploadFile

from ...config import get_settings


def save_upload_file(upload: UploadFile) -> Path:
    """Persist uploaded file without loading entire payload into memory."""
    settings = get_settings()
    dest_dir = settings.storage_dir / "uploads"
    dest_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "").suffix
    filename = f"{uuid.uuid4().hex}{suffix}"
    dest_path = dest_dir / filename
    chunk_size = settings.max_upload_chunk_bytes
    with dest_path.open("wb") as out_file:
        while True:
            chunk = upload.file.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
    return dest_path


def stream_text_file(path: Path) -> Generator[str, None, None]:
    """Yield text chunks from a file with bounded memory usage."""
    settings = get_settings()
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        while True:
            data = handle.read(settings.stream_read_size)
            if not data:
                break
            yield data


def chunk_list(iterable: Iterable, size: int):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


