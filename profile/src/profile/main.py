from contextlib import asynccontextmanager
from profile.api.v1 import profiles
from profile.api.v1.dependencies.services import async_engine
from profile.core.exception_handlers import setup_exception_handlers
from typing import AsyncIterator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)
setup_exception_handlers(app)
app.include_router(router=profiles.router, prefix="/api/v1")


@app.get("/profile/health")
async def check_health():
    return {"status": "ok"}
