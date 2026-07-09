import uuid
from unittest.mock import AsyncMock

import pytest
from notification.db.tables import Notification, NotificationStatus
from notification.schemas.events import BroadcastEvent, UserRegisteredEvent
from notification.services.notification import NotificationService


@pytest.mark.asyncio
async def test_create_broadcast_notifications():
    user_ids = [uuid.uuid4(), uuid.uuid4()]
    notification_ids = [uuid.uuid4(), uuid.uuid4()]

    repo = AsyncMock()
    publisher = AsyncMock()

    async def create_notification(notification: Notification) -> Notification:
        notification.id = notification_ids.pop(0)
        return notification

    repo.create_notification.side_effect = create_notification

    service = NotificationService(repo=repo, publisher=publisher)

    result = await service.create_broadcast_notifications(
        BroadcastEvent(
            user_ids=user_ids,
            template_code="nev_movie",
            payload={"movie_title": "Test title"},
        ),
    )

    assert len(result) == 2
    assert repo.create_notification.await_count == 2
    assert repo.update_status.await_count == 2
    assert repo.commit.await_count == 2
    assert publisher.publish.await_count == 2


@pytest.mark.asyncio
async def test_create_user_registered_notification():
    user_id = uuid.uuid4()
    notification_id = uuid.uuid4()

    repo = AsyncMock()
    publisher = AsyncMock()

    async def create_notification(notification: Notification) -> Notification:
        notification.id = notification_id
        return notification

    repo.create_notification.side_effect = create_notification

    service = NotificationService(repo=repo, publisher=publisher)

    result = await service.create_user_registered_notification(
        UserRegisteredEvent(
            user_id=user_id,
            payload={},
        ),
    )

    assert result == notification_id

    create_notification = repo.create_notification.call_args.kwargs["notification"]
    assert create_notification.user_id == user_id
    assert create_notification.template_code == "welcome"
    assert create_notification.event_type == "user_registered"

    repo.update_status.assert_awaited_once_with(
        notification=create_notification,
        status=NotificationStatus.QUEUED,
    )

    publisher.publish.assert_awaited_once_with(notification_id=notification_id)


@pytest.mark.asyncio
async def test_get_notification_by_id():
    notification_id = uuid.uuid4()
    notification = Notification(
        user_id=uuid.uuid4(),
        template_code="welcome",
        event_type="user_registered",
        payload={},
    )
    notification.id = notification_id

    repo = AsyncMock()
    publisher = AsyncMock()
    repo.get_by_id.return_value = notification

    service = NotificationService(repo=repo, publisher=publisher)

    result = await service.get_notification_by_id(notification_id)

    assert result == notification
    repo.get_by_id.assert_awaited_once_with(notification_id)
