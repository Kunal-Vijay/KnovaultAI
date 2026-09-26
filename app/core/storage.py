import logging
import mimetypes
import os
import re
from typing import Optional, Protocol, runtime_checkable

from app.core.config import settings

logger = logging.getLogger(__name__)

_UNSAFE_PATH_CHARS = re.compile(r"[^\w.\-]+")


def sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename).strip() or "upload"
    cleaned = _UNSAFE_PATH_CHARS.sub("_", base)
    return cleaned[:255]


def build_document_object_key(kb_id: int, filename: str, unique_id: str) -> str:
    """Stable object key: {kb_id}/{unique_id}/{sanitized_filename}."""
    return f"{kb_id}/{unique_id}/{sanitize_filename(filename)}"


@runtime_checkable
class StorageClient(Protocol):
    def save_file(
        self,
        file_content: bytes,
        filename: str,
        *,
        object_key: str,
        content_type: str | None = None,
    ) -> str: ...

    def get_file(self, file_reference: str) -> Optional[bytes]: ...

    def delete_file(self, file_reference: str) -> bool: ...


class LocalFileStorage:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or settings.LOCAL_STORAGE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(
        self,
        file_content: bytes,
        filename: str,
        *,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        del filename, content_type
        file_path = os.path.join(self.base_dir, object_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return object_key

    def get_file(self, file_reference: str) -> Optional[bytes]:
        file_path = os.path.join(self.base_dir, file_reference)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        return None

    def delete_file(self, file_reference: str) -> bool:
        file_path = os.path.join(self.base_dir, file_reference)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


class SupabaseStorageClient:
    def __init__(
        self,
        supabase_url: str,
        service_role_key: str,
        bucket: str,
    ):
        from supabase import create_client

        self._bucket = bucket
        self._client = create_client(supabase_url, service_role_key)

    def save_file(
        self,
        file_content: bytes,
        filename: str,
        *,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        del filename
        mime = content_type or mimetypes.guess_type(object_key)[0] or "application/octet-stream"
        bucket = self._client.storage.from_(self._bucket)
        bucket.upload(
            object_key,
            file_content,
            file_options={"content-type": mime, "upsert": "true"},
        )
        return object_key

    def get_file(self, file_reference: str) -> Optional[bytes]:
        try:
            data = self._client.storage.from_(self._bucket).download(file_reference)
            return bytes(data) if data is not None else None
        except Exception:
            logger.exception("Failed to download object %s from Supabase Storage", file_reference)
            return None

    def delete_file(self, file_reference: str) -> bool:
        try:
            self._client.storage.from_(self._bucket).remove([file_reference])
            return True
        except Exception:
            logger.exception("Failed to delete object %s from Supabase Storage", file_reference)
            return False


def get_storage_client() -> StorageClient:
    backend = (settings.STORAGE_BACKEND or "local").lower()
    if backend == "supabase":
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError(
                "STORAGE_BACKEND=supabase requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"
            )
        return SupabaseStorageClient(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
            settings.SUPABASE_STORAGE_BUCKET,
        )
    return LocalFileStorage()
