from fastapi import FastAPI

from auth.api.v1 import routes

app = FastAPI()


app.include_router(routes.router, prefix="/api/v1/auth")
