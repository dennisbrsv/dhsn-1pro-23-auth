from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from src.config import get_settings
from src.data.users import get_user_by_id

router = APIRouter()


@router.get("/protected")
async def protected_resource(request: Request) -> dict:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing authentication")
    return {"message": "Access granted", "user_id": user_id}


@router.get("/me")
async def me(request: Request) -> dict:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing authentication")
    settings = get_settings()
    user = await get_user_by_id(settings, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.user_id,
        "email": user.email,
        "discord_id": user.discord_id,
        "created_at": user.created_at,
    }
