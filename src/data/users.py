from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from src.config import Settings
from src.data.database import get_connection


@dataclass(frozen=True)
class User:
    user_id: str
    email: str | None
    password_hash: str | None
    discord_id: str | None
    created_at: str


def _row_to_user(row: object) -> User | None:
    if row is None:
        return None
    return User(
        user_id=row["user_id"],
        email=row["email"],
        password_hash=row["password_hash"],
        discord_id=row["discord_id"],
        created_at=row["created_at"],
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_user(
    settings: Settings,
    email: str | None,
    password_hash: str | None,
    discord_id: str | None,
) -> User:
    user_id = str(uuid.uuid4())
    created_at = _now_iso()
    async with get_connection(settings) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, email, password_hash, discord_id, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, email, password_hash, discord_id, created_at),
        )
        await db.commit()
    return User(
        user_id=user_id,
        email=email,
        password_hash=password_hash,
        discord_id=discord_id,
        created_at=created_at,
    )


async def get_user_by_email(settings: Settings, email: str) -> User | None:
    async with get_connection(settings) as db:
        async with db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ) as cursor:
            row = await cursor.fetchone()
    return _row_to_user(row)


async def get_user_by_id(settings: Settings, user_id: str) -> User | None:
    async with get_connection(settings) as db:
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
    return _row_to_user(row)


async def get_user_by_discord_id(settings: Settings, discord_id: str) -> User | None:
    async with get_connection(settings) as db:
        async with db.execute(
            "SELECT * FROM users WHERE discord_id = ?",
            (discord_id,),
        ) as cursor:
            row = await cursor.fetchone()
    return _row_to_user(row)


async def link_discord_id(settings: Settings, user_id: str, discord_id: str) -> None:
    async with get_connection(settings) as db:
        await db.execute(
            "UPDATE users SET discord_id = ? WHERE user_id = ?",
            (discord_id, user_id),
        )
        await db.commit()
