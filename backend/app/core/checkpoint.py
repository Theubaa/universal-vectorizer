import json
from pathlib import Path
from typing import Any, Dict

from ..config import get_settings


class CheckpointStore:
    """Persists ingestion progress so long-running jobs can resume."""

    def __init__(self, job_id: str):
        settings = get_settings()
        self.path: Path = settings.checkpoint_dir / f"{job_id}.json"

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def write(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle)
        tmp_path.replace(self.path)

    def delete(self) -> None:
        if self.path.exists():
            self.path.unlink()


