"""Local evidence file path helpers."""
from pathlib import Path


def resolve_upload(stored_name: str, uploads_dir: Path) -> Path:
    path = (Path(uploads_dir) / Path(stored_name).name).resolve()
    root = Path(uploads_dir).resolve()
    if path.parent != root:
        raise ValueError("Unsafe file path")
    return path
