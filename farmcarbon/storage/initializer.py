"""Initialise local JSON files and upload/export directories."""
from config.settings import settings
from farmcarbon.storage.json_store import JsonStore


def initialize_storage() -> JsonStore:
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    return JsonStore(settings.data_dir)
