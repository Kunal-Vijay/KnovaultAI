import os
from typing import Optional

from app.core.config import settings


class LocalFileStorage:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = base_dir or settings.LOCAL_STORAGE_DIR
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, file_content: bytes, filename: str) -> str:
        """Saves a file to local storage and returns its reference (path)."""
        file_path = os.path.join(self.base_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return os.path.relpath(file_path, self.base_dir) # Return relative path as reference

    def get_file(self, file_reference: str) -> Optional[bytes]:
        """Retrieves a file from local storage using its reference."""
        file_path = os.path.join(self.base_dir, file_reference)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        return None

    def delete_file(self, file_reference: str) -> bool:
        """Deletes a file from local storage."""
        file_path = os.path.join(self.base_dir, file_reference)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

def get_storage_client():
    return LocalFileStorage()
