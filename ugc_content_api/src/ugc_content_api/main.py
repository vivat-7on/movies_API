from fastapi import FastAPI

from ugc_content_api.api.v1.ratings import router

app = FastAPI()


app.include_router(router=router, prefix="/api/v1")
