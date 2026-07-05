from fastapi import FastAPI

from .v1.events import router

app = FastAPI()

app.include_router(router=router, prefix="/api/v1/notification")


@app.get("/notification/health")
async def check_health():
    return {"status": "ok"}
