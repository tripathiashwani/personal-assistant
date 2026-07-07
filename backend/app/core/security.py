"""
Low-level security primitives: password hashing and JWT encode/decode.

This module knows nothing about the User model or the database — it just
turns plain passwords into hashes (and back, via verification) and turns
a payload dict into a signed token (and back). AuthService is the only
caller; keeping this separate means we could swap bcrypt for argon2, or
add a refresh-token scheme, without touching anything above this layer.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Creates a signed JWT. `subject` is typically the user's id (as a string)
    and ends up in the `sub` claim, which `decode_access_token` reads back.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Returns the `sub` claim (user id) if the token is valid and unexpired,
    otherwise None. Callers (api/deps.py) turn a None into a 401.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
