import uuid

from fastapi import APIRouter, Depends
from starlette import status

from notification.api.deps import create_notification_service
from notification.schemas.events import BroadcastEvent
from notification.services.notification import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post("/broadcast", status_code=status.HTTP_201_CREATED)
async def broadcast(
    data: BroadcastEvent,
    service: NotificationService = Depends(create_notification_service),
) -> dict[str, list[uuid.UUID]]:
    notification_ids = await service.create_broadcast_notifications(data=data)

    return {"notifications": notification_ids}
