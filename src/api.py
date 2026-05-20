from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, Optional

from fastapi import FastAPI

from src.config import get_settings
from src.data.database import init_db
from src.middleware.auth import JwtAuthMiddleware
from src.routes import auth, index, protected
from src.config import Settings


def create_app() -> FastAPI:
    settings = get_settings()
    lifespan = _auth_lifespan(settings)

    app = FastAPI(title="Auth Demo", lifespan=lifespan)

    _add_routes(app)
    app.include_router(index.router)
    app.include_router(protected.router)
    _add_middleware(app, settings)

    return app

def _add_routes(app: FastAPI) -> None:
    app.include_router(auth.router)

def _add_middleware(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(JwtAuthMiddleware, settings=settings)

Lifespan = Callable[[FastAPI], AsyncIterator[None]]


def _auth_lifespan(settings: Settings) -> Lifespan:
    @asynccontextmanager
    async def auth_lifespan(app: FastAPI) -> AsyncIterator[None]:
        await init_db(settings)
        yield

    return auth_lifespan


def _compose_lifespan(first: Lifespan, second: Lifespan) -> Lifespan:
    @asynccontextmanager
    async def merged_lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with first(app):
            async with second(app):
                yield

    return merged_lifespan


def _merge_lifespan(app: FastAPI, extra: Lifespan) -> None:
    existing = app.router.lifespan_context
    if existing is None:
        app.router.lifespan_context = extra
        return

    app.router.lifespan_context = _compose_lifespan(existing, extra)


def inject_auth(app: FastAPI, extra_lifespan: Optional[Lifespan] = None) -> FastAPI:
    settings = get_settings()
    _add_routes(app)
    _add_middleware(app, settings)

    auth_lifespan = _auth_lifespan(settings)
    merged = auth_lifespan
    if extra_lifespan is not None:
        merged = _compose_lifespan(merged, extra_lifespan)

    _merge_lifespan(app, merged)

    return app

app = create_app()
