"""Repository helpers over local JSON files."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any
from farmcarbon.storage.json_store import JsonStore


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class Repository:
    def __init__(self, store: JsonStore):
        self.store = store

    def list(self, collection: str, **filters: Any) -> list[dict[str, Any]]:
        rows = self.store.all(collection)
        for key, value in filters.items():
            rows = [r for r in rows if r.get(key) == value]
        return rows

    def get(self, collection: str, record_id: str) -> dict[str, Any] | None:
        return self.store.get(collection, record_id)

    def create(self, collection: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {"id": str(uuid4()), **payload}
        record.setdefault("created_at", now_iso())
        return self.store.create(collection, record)

    def update(self, collection: str, record_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        changes = {**changes, "updated_at": now_iso()}
        return self.store.update(collection, record_id, changes)

    def delete(self, collection: str, record_id: str) -> bool:
        return self.store.delete(collection, record_id)

    def audit(self, farm_id: str | None, entity_type: str, entity_id: str,
              action: str, description: str, source_mode: str = "USER") -> None:
        self.create("audit_events", {
            "farm_id": farm_id, "entity_type": entity_type, "entity_id": entity_id,
            "action": action, "description": description, "source_mode": source_mode,
        })

    def delete_farm_cascade(self, farm_id: str, uploads_dir=None) -> None:
        """Remove a farm and its child records; attachment files are removed when possible."""
        evidence = self.list("evidence_files", farm_id=farm_id)
        for item in evidence:
            path = item.get("stored_path")
            if path and uploads_dir:
                try:
                    from pathlib import Path
                    p = (Path(uploads_dir) / Path(path).name).resolve()
                    if p.parent == Path(uploads_dir).resolve() and p.exists():
                        p.unlink()
                except OSError:
                    pass
        for collection in ("soil_samples", "satellite_observations", "practices", "evidence_files", "mrv_reviews"):
            self.store.replace_all(collection, [r for r in self.store.all(collection) if r.get("farm_id") != farm_id])
        self.store.replace_all("audit_events", [r for r in self.store.all("audit_events") if r.get("farm_id") != farm_id])
        self.delete("farms", farm_id)
