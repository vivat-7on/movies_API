from fastapi import FastAPI

from auth.api.v1 import auth, roles

app = FastAPI()


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
