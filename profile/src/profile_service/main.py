from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from profile_service.api.v1 import profiles
from profile_service.core.config import get_app_settings
from profile_service.core.exception_handlers import setup_exception_handlers
from profile_service.db.runtime import async_engine

app_settings = get_app_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await async_engine.dispose()


app = FastAPI(
    docs_url="/profiles/docs" if app_settings.DEBUG else None,
    openapi_url="/profiles/openapi.json" if app_settings.DEBUG else None,
    lifespan=lifespan,
)

setup_exception_handlers(app)
app.include_router(router=profiles.router, prefix="/api/v1")


@app.get("/api/v1/profiles/health")
async def check_health() -> dict[str, str]:
    return {"status": "ok"}
