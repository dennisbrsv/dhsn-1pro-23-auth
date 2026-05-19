from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.auth.jwt import JwtError, decode_jwt
from src.config import Settings


class JwtAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        settings: Settings,
        protected_prefixes: tuple[str, ...] = ("/protected", "/me"),
    ) -> None:
        super().__init__(app)
        self._settings = settings
        self._protected_prefixes = protected_prefixes

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self._is_protected_path(request.url.path):
            return await call_next(request)
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Missing bearer token"}, status_code=401
            )
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_jwt(token, self._settings.secret_key)
        except JwtError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=401)
        subject = payload.get("sub")
        if not subject:
            return JSONResponse({"detail": "Invalid token payload"}, status_code=401)
        request.state.user_id = subject
        return await call_next(request)

    def _is_protected_path(self, path: str) -> bool:
        return path.startswith(self._protected_prefixes)
