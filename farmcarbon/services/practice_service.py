"""Agricultural practice and evidence operations."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
import re
from farmcarbon.storage.repository import Repository

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".csv", ".pdf"}

class PracticeService:
    def __init__(self, repo: Repository, uploads_dir: Path):
        self.repo, self.uploads_dir = repo, Path(uploads_dir)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, uploaded_file, farm_id: str, practice_id: str | None = None):
        original = Path(uploaded_file.name).name
        suffix = Path(original).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported evidence file type: {suffix or 'no extension'}")
        safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(original).stem).strip("._") or "evidence"
        stored_name = f"{uuid4().hex}_{safe_stem[:50]}{suffix}"
        destination = (self.uploads_dir / stored_name).resolve()
        if destination.parent != self.uploads_dir.resolve():
            raise ValueError("Unsafe upload path")
        destination.write_bytes(uploaded_file.getvalue())
        evidence = self.repo.create("evidence_files", {
            "farm_id": farm_id, "practice_id": practice_id, "file_name": original,
            "stored_path": stored_name, "file_type": suffix.lstrip("."),
        })
        return evidence
