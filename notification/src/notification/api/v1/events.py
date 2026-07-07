import uuid

from fastapi import APIRouter, Depends
from starlette import status

from notification.api.deps import create_notification_service
from notification.schemas.events import NewMovieEvent, UserRegisteredEvent
from notification.services.notification import NotificationService

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


@router.post(
    "/new-movie",
    status_code=status.HTTP_201_CREATED,
)
async def send_new_movie(
    data: NewMovieEvent,
    service: NotificationService = Depends(create_notification_service),
) -> dict[str, list[uuid.UUID]]:
    notification_id = await service.create_new_movie_notification(data=data)

    return {"notification_id": notification_id}
