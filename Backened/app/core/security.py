"""Password hashing and JWT helpers for account endpoints."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import InvalidTokenError

from app.core.config import settings

ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(hours=24)


def get_jwt_secret() -> str:
    secret = settings.JWT_SECRET_KEY.strip()
    if len(secret) < 32 or secret.lower().startswith(("replace_", "change_me")):
        raise RuntimeError("Set a random JWT_SECRET_KEY of at least 32 characters in .env")
    return secret


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password must be at most 72 UTF-8 bytes")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > 72:
        return False
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + TOKEN_LIFETIME
    return jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, get_jwt_secret(), algorithms=[ALGORITHM])


__all__ = ["InvalidTokenError", "create_access_token", "decode_access_token", "hash_password", "verify_password"]
