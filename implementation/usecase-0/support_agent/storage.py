import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from config import DATA_DIR


class JsonStore:
    """Tiny JSON persistence layer for Render-friendly demo storage."""

    def __init__(self, data_dir: Path | str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, threading.Lock] = {}

    def _path(self, name: str) -> Path:
        if not name.endswith(".json"):
            name = f"{name}.json"
        return self.data_dir / name

    def _lock_for(self, name: str) -> threading.Lock:
        self._locks.setdefault(name, threading.Lock())
        return self._locks[name]

    def read(self, name: str, default: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            self.write(name, default)
            return default
        with self._lock_for(name):
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)

    def write(self, name: str, payload: Any) -> None:
        path = self._path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock_for(name):
            fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as file:
                    json.dump(payload, file, indent=2, sort_keys=True)
                    file.write("\n")
                os.replace(tmp_name, path)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)

    def update(self, name: str, default: Any, updater):
        with self._lock_for(name):
            path = self._path(name)
            if path.exists():
                with path.open("r", encoding="utf-8") as file:
                    payload = json.load(file)
            else:
                payload = default
            result = updater(payload)
            fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as file:
                    json.dump(payload, file, indent=2, sort_keys=True)
                    file.write("\n")
                os.replace(tmp_name, path)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            return result

