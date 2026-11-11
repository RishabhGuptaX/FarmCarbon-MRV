"""Small atomic JSON document store used instead of a SQL database.

Each collection is one JSON array under storage/data. Writes use a temporary file
and os.replace so an interrupted write does not leave a half-written document.
This is intended for a single-user/local MVP, not concurrent multi-server use.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any

COLLECTIONS = (
    "farms", "soil_samples", "satellite_observations", "practices",
    "evidence_files", "mrv_reviews", "audit_events",
)

class JsonStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        for name in COLLECTIONS:
            path = self._path(name)
            if not path.exists():
                self._write(name, [])

    def _path(self, collection: str) -> Path:
        if collection not in COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection}")
        return self.data_dir / f"{collection}.json"

    def _write(self, collection: str, records: list[dict[str, Any]]) -> None:
        path = self._path(collection)
        temp = path.with_suffix(path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2, default=str)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)

    def all(self, collection: str) -> list[dict[str, Any]]:
        with self._lock:
            path = self._path(collection)
            try:
                with path.open("r", encoding="utf-8") as handle:
                    value = json.load(handle)
                if not isinstance(value, list):
                    raise ValueError(f"{path.name} must contain a JSON array")
                return value
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Stored file {path.name} is corrupted: {exc}") from exc

    def replace_all(self, collection: str, records: list[dict[str, Any]]) -> None:
        with self._lock:
            self._write(collection, records)

    def get(self, collection: str, record_id: str) -> dict[str, Any] | None:
        return next((r for r in self.all(collection) if str(r.get("id")) == str(record_id)), None)

    def create(self, collection: str, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            records = self.all(collection)
            records.append(record)
            self._write(collection, records)
        return record

    def update(self, collection: str, record_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            records = self.all(collection)
            updated = None
            for index, record in enumerate(records):
                if str(record.get("id")) == str(record_id):
                    records[index] = {**record, **changes}
                    updated = records[index]
                    break
            if updated is not None:
                self._write(collection, records)
            return updated

    def delete(self, collection: str, record_id: str) -> bool:
        with self._lock:
            records = self.all(collection)
            remaining = [r for r in records if str(r.get("id")) != str(record_id)]
            if len(remaining) == len(records):
                return False
            self._write(collection, remaining)
            return True

    def clear(self) -> None:
        with self._lock:
            for name in COLLECTIONS:
                self._write(name, [])
