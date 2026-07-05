from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/user-registred")
async def send_welcome_message():
    return {"message": "Welcome Message"}


@router.post("/new-movie")
async def send_new_movie():
    return {"message": "Welcome Message"}
