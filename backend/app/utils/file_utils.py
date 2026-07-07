"""
Local file storage helpers.

All uploaded files live under settings.STORAGE_DIR, namespaced by user id
so one user's files are never reachable through another user's paths.
This is the ONLY module that touches the filesystem directly — when we
move to S3/cloud storage later, only this file changes.
"""
import uuid
from pathlib import Path

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def get_user_storage_dir(user_id: uuid.UUID) -> Path:
    user_dir = Path(settings.STORAGE_DIR) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def build_storage_path(user_id: uuid.UUID, document_id: uuid.UUID, original_filename: str) -> Path:
    ext = Path(original_filename).suffix.lower()
    return get_user_storage_dir(user_id) / f"{document_id}{ext}"


def save_file_bytes(path: Path, content: bytes) -> None:
    path.write_bytes(content)


def delete_file(path: Path) -> None:
    """Deletes the file if it exists. Never raises if it's already gone."""
    p = Path(path)
    if p.exists():
        p.unlink()


def is_allowed_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def extension_to_document_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext in (".md", ".markdown"):
        return "markdown"
    raise ValueError(f"Unsupported file extension: {ext}")
