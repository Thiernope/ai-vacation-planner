from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_application_settings

# bcrypt rejects passwords longer than 72 bytes. Surface a clear error at the
# application boundary rather than letting bcrypt raise mid-hash.
BCRYPT_MAX_PASSWORD_BYTES = 72


class PasswordTooLongError(ValueError):
    """Raised when a password exceeds bcrypt's 72-byte input limit."""


def hash_password(plain_text_password: str) -> str:
    """Return a bcrypt hash (as UTF-8 text) for the given plain-text password."""
    password_bytes = plain_text_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise PasswordTooLongError(
            f"Password must be {BCRYPT_MAX_PASSWORD_BYTES} bytes or fewer."
        )
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_text_password: str, stored_password_hash: str) -> bool:
    """Return True if the plain-text password matches the stored bcrypt hash."""
    password_bytes = plain_text_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(password_bytes, stored_password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash on disk — treat as a verification failure rather than a crash.
        return False


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Sign and return a JWT access token for the given user identifier (subject)."""
    settings = get_application_settings()

    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=settings.access_token_expire_minutes)

    token_claims: dict[str, Any] = {
        "sub": subject,
        "iat": issued_at,
        "exp": expires_at,
    }
    if extra_claims:
        token_claims.update(extra_claims)

    return jwt.encode(token_claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT, returning its claims dict.

    Raises `JWTError` for invalid or expired tokens — callers translate that into
    an HTTP 401 response.
    """
    settings = get_application_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
    "PasswordTooLongError",
]
