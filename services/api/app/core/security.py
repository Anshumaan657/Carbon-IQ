from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from jwt.exceptions import InvalidTokenError as PyJWTInvalidTokenError
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.models.enums import UserRole


password_hash = PasswordHash.recommended()


class InvalidAccessTokenError(ValueError):
    """Raised when an access token is invalid, expired, or has the wrong type."""


@dataclass(frozen=True)
class AccessTokenClaims:
    subject: UUID
    role: UserRole
    token_id: UUID


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return password_hash.verify(password, encoded_hash)


def create_access_token(
    user_id: UUID,
    role: UserRole,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "type": "access",
        "jti": str(uuid4()),
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> AccessTokenClaims:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "role", "type", "jti", "iat", "exp"]},
        )
        if payload["type"] != "access":
            raise InvalidAccessTokenError("unexpected token type")
        return AccessTokenClaims(
            subject=UUID(payload["sub"]),
            role=UserRole(payload["role"]),
            token_id=UUID(payload["jti"]),
        )
    except (PyJWTInvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError("invalid access token") from exc


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def digest_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
