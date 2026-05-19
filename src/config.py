from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    secret_key: str
    access_token_ttl_minutes: int
    database_url: str
    discord_client_id: str
    discord_client_secret: str
    discord_redirect_uri: str
    discord_authorize_url: str
    discord_token_url: str


def get_settings() -> Settings:
    load_dotenv()
    
    return Settings(
        secret_key=os.getenv("SECRET_KEY", "dev-secret-change"),
        access_token_ttl_minutes=int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "60")),
        database_url=os.getenv("DATABASE_URL", "./auth.db"),
        discord_client_id=os.getenv("DISCORD_CLIENT_ID", ""),
        discord_client_secret=os.getenv("DISCORD_CLIENT_SECRET", ""),
        discord_redirect_uri=os.getenv("DISCORD_REDIRECT_URI", ""),
        discord_authorize_url=os.getenv(
            "DISCORD_AUTHORIZE_URL", "https://discord.com/api/oauth2/authorize"
        ),
        discord_token_url=os.getenv(
            "DISCORD_TOKEN_URL", "https://discord.com/api/oauth2/token"
        ),
    )
