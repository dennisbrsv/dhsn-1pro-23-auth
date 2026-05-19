from __future__ import annotations

from contextlib import asynccontextmanager

import aiosqlite

from src.config import Settings


async def init_db(settings: Settings) -> None:
    async with aiosqlite.connect(settings.database_url) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                discord_id TEXT UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()


@asynccontextmanager
async def get_connection(settings: Settings):
    async with aiosqlite.connect(settings.database_url) as db:
        db.row_factory = aiosqlite.Row
        yield db
