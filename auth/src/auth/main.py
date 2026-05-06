import os

from fastapi import FastAPI

from auth.api.v1 import auth, roles, users
from auth.core.exception_handlers import setup_exception_handlers

DEBUG = os.getenv("DEBUG", "true").lower() == "true"


app = FastAPI(
    docs_url="/docs" if DEBUG else None,
    openapi_url="/auth/openapi.json" if DEBUG else None,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


setup_exception_handlers(app)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
