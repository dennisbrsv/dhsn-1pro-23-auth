from __future__ import annotations

import time

from src.auth.jwt import encode_jwt
from src.auth.passwords import hash_password, verify_password
from src.config import Settings
from src.data import users


class AuthError(Exception):
    pass


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def issue_access_token(user_id: str, settings: Settings) -> str:
    now = int(time.time())
    ttl_seconds = settings.access_token_ttl_minutes * 60
    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return encode_jwt(claims, settings.secret_key)


async def register_local_user(
    settings: Settings, email: str, password: str
) -> users.User:
    email = _normalize_email(email)
    if await users.get_user_by_email(settings, email):
        raise AuthError("Email already registered")
    password_hash = hash_password(password)
    return await users.create_user(settings, email, password_hash, None)


async def authenticate_local_user(
    settings: Settings, email: str, password: str
) -> users.User | None:
    email = _normalize_email(email)
    user = await users.get_user_by_email(settings, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def register_or_login_discord_user(
    settings: Settings, discord_id: str, email: str | None
) -> users.User:
    existing = await users.get_user_by_discord_id(settings, discord_id)
    if existing:
        return existing
    normalized_email = _normalize_email(email) if email else None
    return await users.create_user(settings, normalized_email, None, discord_id)
