from fastapi import FastAPI

from ugc_content_api.api.v1.ratings import router
from ugc_content_api.api.v1.reviews import movie_router, review_router
from ugc_content_api.core.exception_handlers import setup_exception_handlers

app = FastAPI()

setup_exception_handlers(app)

app.include_router(router=router, prefix="/api/v1")
app.include_router(router=review_router, prefix="/api/v1")
app.include_router(router=movie_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
