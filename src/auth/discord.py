from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import aiohttp

from src.config import Settings


@dataclass(frozen=True)
class DiscordIdentity:
    discord_id: str
    email: str | None


def build_discord_authorize_url(state: str, settings: Settings) -> str:
    params = {
        "client_id": settings.discord_client_id,
        "redirect_uri": settings.discord_redirect_uri,
        "response_type": "code",
        "scope": "identify email",
        "state": state,
    }
    return f"{settings.discord_authorize_url}?{urlencode(params)}"


async def resolve_identity_from_code(
    code: str, settings: Settings
) -> DiscordIdentity:
    if not settings.discord_client_id or not settings.discord_client_secret:
        raise RuntimeError("Discord OAuth credentials are missing")
    if not settings.discord_redirect_uri:
        raise RuntimeError("Discord redirect URI is missing")

    token_payload = {
        "client_id": settings.discord_client_id,
        "client_secret": settings.discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.discord_redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            settings.discord_token_url,
            data=token_payload,
            headers=headers,
        ) as token_response:
            token_data = await token_response.json()
            if token_response.status >= 400:
                raise RuntimeError(
                    f"Discord token exchange failed: {token_data}"
                )
        access_token = token_data.get("access_token")
        if not access_token:
            raise RuntimeError("Discord token response missing access_token")

        async with session.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as user_response:
            user_data = await user_response.json()
            if user_response.status >= 400:
                raise RuntimeError(
                    f"Discord user lookup failed: {user_data}"
                )

    discord_id = str(user_data.get("id", "")).strip()
    if not discord_id:
        raise RuntimeError("Discord user response missing id")
    email = user_data.get("email")
    return DiscordIdentity(discord_id=discord_id, email=email)
