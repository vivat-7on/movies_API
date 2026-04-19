from fastapi import FastAPI

from auth.api.v1 import auth, roles, users

app = FastAPI(
    docs_url="/docs",
    openapi_url="/auth/openapi.json",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
