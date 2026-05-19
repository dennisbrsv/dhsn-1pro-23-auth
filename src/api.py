from __future__ import annotations

from fastapi import FastAPI

from src.config import get_settings
from src.data.database import init_db
from src.middleware.auth import JwtAuthMiddleware
from src.routes import auth, index, protected


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Auth Demo")

    app.add_middleware(JwtAuthMiddleware, settings=settings)

    app.include_router(index.router)
    app.include_router(auth.router)
    app.include_router(protected.router)

    @app.on_event("startup")
    async def startup() -> None:
        await init_db(settings)

    return app


app = create_app()
