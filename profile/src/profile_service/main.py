import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from profile_service.api.v1 import profiles
from profile_service.core.exception_handlers import setup_exception_handlers
from profile_service.db.runtime import async_engine

DEBUG = os.getenv("DEBUG", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await async_engine.dispose()


app = FastAPI(
    docs_url="/profiles/docs" if DEBUG else None,
    openapi_url="/profiles/openapi.json" if DEBUG else None,
    lifespan=lifespan,
)

setup_exception_handlers(app)
app.include_router(router=profiles.router, prefix="/api/v1")


@app.get("/profile/health")
async def check_health():
    return {"status": "ok"}
