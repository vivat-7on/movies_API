import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from notification.api.deps import create_notification_service
from notification.schemas.events import BroadcastEvent, NotificationResponse
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


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
async def get_notification(
    notification_id: int,
    service: NotificationService = Depends(create_notification_service),
) -> NotificationResponse:
    notificaton = service.get_notification_by_id(
        notification_id=notification_id,
    )

    if notificaton is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return NotificationResponse(
        user_id=notificaton.user_id,
        status=notificaton.status,
        created_at=notificaton.created_at,
        last_error=notificaton.last_error,
        sent_at=notificaton.sent_at,
    )
