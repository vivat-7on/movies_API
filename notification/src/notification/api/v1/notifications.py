import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from notification.api.deps import create_notification_service
from notification.api.security import verify_service_token
from notification.db.tables import Notification
from notification.schemas.events import BroadcastEvent, NotificationResponse
from notification.services.notification import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    dependencies=[Depends(verify_service_token)],
)


@router.post("/broadcast", status_code=status.HTTP_201_CREATED)
async def broadcast(
    data: BroadcastEvent,
    service: NotificationService = Depends(create_notification_service),
) -> dict[str, list[uuid.UUID]]:
    notification_ids = await service.create_broadcast_notifications(data=data)

    return {"notifications": notification_ids}


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
async def get_notification(
    notification_id: uuid.UUID,
    service: NotificationService = Depends(create_notification_service),
) -> Notification:
    notification = await service.get_notification_by_id(
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return notification
