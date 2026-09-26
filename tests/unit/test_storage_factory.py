from unittest.mock import MagicMock, patch
import sys

import pytest

from app.core.storage import LocalFileStorage, SupabaseStorageClient, get_storage_client


def test_get_storage_client_defaults_to_local():
    with patch("app.core.storage.settings") as mock_settings:
        mock_settings.STORAGE_BACKEND = "local"
        client = get_storage_client()
        assert isinstance(client, LocalFileStorage)


def test_get_storage_client_supabase():
    with patch("app.core.storage.settings") as mock_settings:
        mock_settings.STORAGE_BACKEND = "supabase"
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "service-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "documents"
        mock_client = MagicMock()
        fake_module = MagicMock(create_client=MagicMock(return_value=mock_client))
        with patch.dict(sys.modules, {"supabase": fake_module}):
            client = get_storage_client()
            assert isinstance(client, SupabaseStorageClient)
            fake_module.create_client.assert_called_once_with(
                "https://example.supabase.co",
                "service-key",
            )


def test_get_storage_client_supabase_missing_credentials():
    with patch("app.core.storage.settings") as mock_settings:
        mock_settings.STORAGE_BACKEND = "supabase"
        mock_settings.SUPABASE_URL = ""
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = ""
        with pytest.raises(ValueError, match="SUPABASE_URL"):
            get_storage_client()
