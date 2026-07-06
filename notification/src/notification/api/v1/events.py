import uuid

from fastapi import APIRouter, Depends
from notification.api.deps import create_notification_service
from notification.schemas.events import UserRegisteredEvent
from notification.services.notification import NotificationService
from starlette import status

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/user-registered",
    status_code=status.HTTP_201_CREATED,
)
async def send_welcome_message(
    data: UserRegisteredEvent,
    service: NotificationService = Depends(create_notification_service),
) -> dict[str, uuid.UUID]:
    notification_id = await service.create_user_registered_notification(
        data=data,
    )

    return {"notification_id": notification_id}


@router.post("/new-movie")
async def send_new_movie():
    return {"message": "Welcome Message"}
