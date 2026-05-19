from __future__ import annotations

from fastapi import HTTPException, Request

from src.auth.jwt import JwtError, decode_jwt
from src.config import Settings


def get_current_user_id(request: Request, settings: Settings) -> str:
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_jwt(token, settings.secret_key)
    except JwtError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return subject
