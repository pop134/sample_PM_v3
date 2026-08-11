"""Application entrypoint and FastAPI app factory."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, health, locations, weather
from app.core.config import get_settings
from app.core.openapi import (
    API_DESCRIPTION,
    CONTACT,
    LICENSE,
    TAGS_METADATA,
)
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev/test convenience: ensure tables exist. Production uses migrations (WBS 1.7).
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=API_DESCRIPTION,
        openapi_tags=TAGS_METADATA,
        contact=CONTACT,
        license_info=LICENSE,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(weather.router, prefix="/api")
    app.include_router(locations.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {"service": settings.app_name, "docs": "/docs"}

    return app


app = create_app()
