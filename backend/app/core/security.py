"""Password hashing and JWT handling."""

from datetime import timedelta
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import settings
from app.core.time import utcnow
from app.db.models import User

_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password with Argon2id."""

    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password without leaking which part failed."""

    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(user: User) -> str:
    """Create a short-lived access token for a user."""

    issued_at = utcnow()
    expires_at = issued_at + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "org": user.organisation_id,
        "role": user.role,
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a token. Raises ``jwt.InvalidTokenError`` on failure."""

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
        options={"require": ["exp", "iat", "sub", "iss", "aud"]},
    )
