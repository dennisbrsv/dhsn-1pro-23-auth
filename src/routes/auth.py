from __future__ import annotations

import secrets

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.auth.discord import build_discord_authorize_url, resolve_identity_from_code
from src.auth.service import (
    AuthError,
    authenticate_local_user,
    issue_access_token,
    register_local_user,
    register_or_login_discord_user,
)
from src.config import get_settings

router = APIRouter()


async def _read_credentials(request: Request) -> tuple[str, str]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
    elif content_type.startswith("application/x-www-form-urlencoded"):
        payload = await request.form()
    else:
        raise HTTPException(status_code=415, detail="Unsupported content type")
    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", "")).strip()
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")
    return email, password


@router.post("/auth/register")
async def register(request: Request) -> JSONResponse:
    settings = get_settings()
    email, password = await _read_credentials(request)
    try:
        user = await register_local_user(settings, email, password)
    except AuthError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    token = issue_access_token(user.user_id, settings)
    return JSONResponse({"access_token": token, "token_type": "bearer"})


@router.post("/auth/login")
async def login(request: Request) -> JSONResponse:
    settings = get_settings()
    email, password = await _read_credentials(request)
    user = await authenticate_local_user(settings, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = issue_access_token(user.user_id, settings)
    return JSONResponse({"access_token": token, "token_type": "bearer"})


@router.get("/auth/discord/login")
async def discord_login() -> RedirectResponse:
    settings = get_settings()
    state = secrets.token_urlsafe(24)
    redirect_url = build_discord_authorize_url(state, settings)
    response = RedirectResponse(url=redirect_url)
    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        samesite="lax",
        max_age=600,
    )
    return response


@router.get("/auth/discord/callback", response_model=None)
async def discord_callback(request: Request) -> RedirectResponse:
    settings = get_settings()
    query_state = request.query_params.get("state")
    cookie_state = request.cookies.get("oauth_state")
    if not query_state or cookie_state != query_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    try:
        identity = await resolve_identity_from_code(code, settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    user = await register_or_login_discord_user(
        settings, identity.discord_id, identity.email
    )
    token = issue_access_token(user.user_id, settings)
    response = RedirectResponse(url=f"/?token={token}")
    response.delete_cookie("oauth_state")
    return response
