import asyncio
from datetime import timedelta
import pytest
from fastapi import HTTPException

from app.core.security import (
    can_upload_from_token_payload,
    create_access_token,
    decode_access_token_payload,
    require_can_upload,
)


def test_can_upload_from_token_payload_defaults_true():
    assert can_upload_from_token_payload({}) is True
    assert can_upload_from_token_payload({"can_upload": True}) is True


def test_can_upload_from_token_payload_false():
    assert can_upload_from_token_payload({"can_upload": False}) is False


def test_password_token_includes_can_upload_true():
    token = create_access_token(
        data={"sub": "demo", "user_id": 1, "can_upload": True},
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_access_token_payload(token)
    assert payload["can_upload"] is True
    assert can_upload_from_token_payload(payload) is True


def test_demo_token_includes_can_upload_false():
    token = create_access_token(
        data={"sub": "demo", "user_id": 1, "can_upload": False},
        expires_delta=timedelta(minutes=5),
    )
    payload = decode_access_token_payload(token)
    assert payload["can_upload"] is False
    assert can_upload_from_token_payload(payload) is False


def test_require_can_upload_blocks_demo_token():
    token = create_access_token(
        data={"sub": "demo", "user_id": 1, "can_upload": False},
        expires_delta=timedelta(minutes=5),
    )

    async def run():
        await require_can_upload(token=token)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(run())
    assert exc.value.status_code == 403
    assert "demo" in exc.value.detail.lower()


def test_require_can_upload_allows_password_token():
    token = create_access_token(
        data={"sub": "demo", "user_id": 1, "can_upload": True},
        expires_delta=timedelta(minutes=5),
    )

    async def run():
        await require_can_upload(token=token)

    asyncio.run(run())
