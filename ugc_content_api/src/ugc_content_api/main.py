import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ugc_content_api.api.v1.bookmarks import (
    bookmarks_router,
    movie_bookmarks_router,
)
from ugc_content_api.api.v1.ratings import router
from ugc_content_api.api.v1.reviews import movie_router, review_router
from ugc_content_api.core.connect import create_client
from ugc_content_api.core.exception_handlers import setup_exception_handlers
from ugc_content_api.core.indexes import create_indexes
from ugc_content_api.core.settings import get_mongo_settings

DEBUG = os.getenv("DEBUG", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_mongo_settings()
    client = create_client(settings)
    db = client[settings.MONGO_DB]

    await create_indexes(db)

    app.state.mongo_client = client
    app.state.mongo_db = db

    yield

    await client.close()


app = FastAPI(
    docs_url="/ugc-content/docs" if DEBUG else None,
    openapi_url="/ugc-content/openapi.json" if DEBUG else None,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.include_router(router=router, prefix="/api/v1/ugc-content")
app.include_router(router=review_router, prefix="/api/v1/ugc-content")
app.include_router(router=movie_router, prefix="/api/v1/ugc-content")
app.include_router(router=movie_bookmarks_router, prefix="/api/v1/ugc-content")
app.include_router(router=bookmarks_router, prefix="/api/v1/ugc-content")


@app.get("/api/v1/ugc-content/health")
def health():
    return {"status": "ok"}
