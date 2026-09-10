from datetime import timedelta
from uuid import uuid4

import pytest

from app.core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    digest_refresh_token,
    generate_refresh_token,
    hash_password,
    verify_password,
)
from app.models.enums import UserRole


def test_password_is_hashed_and_verified() -> None:
    encoded = hash_password("correct horse battery staple")

    assert encoded != "correct horse battery staple"
    assert verify_password("correct horse battery staple", encoded) is True
    assert verify_password("incorrect password", encoded) is False


def test_access_token_round_trip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id, UserRole.ADMIN)

    claims = decode_access_token(token)

    assert claims.subject == user_id
    assert claims.role is UserRole.ADMIN


def test_expired_access_token_is_rejected() -> None:
    token = create_access_token(
        uuid4(),
        UserRole.BUYER,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token)


def test_invalid_access_token_is_rejected() -> None:
    with pytest.raises(InvalidAccessTokenError):
        decode_access_token("not-a-jwt")


def test_refresh_tokens_are_random_and_digested() -> None:
    first = generate_refresh_token()
    second = generate_refresh_token()

    assert first != second
    assert len(digest_refresh_token(first)) == 64
    assert first not in digest_refresh_token(first)
