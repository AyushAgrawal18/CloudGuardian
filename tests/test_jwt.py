
from datetime import timedelta

import jwt
import pytest

from backend.app.core.jwt import (
    create_access_token,
    decode_access_token,
)


def test_create_and_decode_access_token():
    token = create_access_token(subject="1")

    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_expired_access_token_is_rejected():
    token = create_access_token(
        subject="1",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_token_is_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid.token.value")


def test_token_with_wrong_secret_is_rejected(monkeypatch):
    import backend.app.core.jwt as jwt_module

    token = create_access_token(subject="1")

    monkeypatch.setattr(
        jwt_module,
        "JWT_SECRET_KEY",
        "wrong-secret-key-for-testing-only-32-chars",
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)
