import datetime
import uuid

import pytest
from app.schemas import EventIn, EventMessage
from pydantic import ValidationError


def test_event_in_validates_correct_event():
    event = EventIn.model_validate(
        {
            "event_type": "page_view",
            "anonymous_id": "anon-1",
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert event.event_type == "page_view"
    assert isinstance(event.timestamp, datetime.datetime)


def test_event_in_rejects_invalid_event_type():
    with pytest.raises(ValidationError):
        EventIn.model_validate(
            {
                "event_type": "invalid_event_type",
                "anonymous_id": "anon-1",
                "timestamp": "2026-05-22T12:00:00Z",
                "payload": {"page_url": "/movies/123"},
            },
        )


def test_event_message_accepts_user_id():
    user_id = uuid.uuid4()
    event = EventMessage.model_validate(
        {
            "event_type": "page_view",
            "user_id": user_id,
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert event.user_id == user_id


def test_event_in_does_not_accept_user_id():
    with pytest.raises(ValidationError):
        user_id = uuid.uuid4()
        EventIn.model_validate(
            {
                "event_type": "page_view",
                "user_id": user_id,
                "timestamp": "2026-05-22T12:00:00Z",
                "payload": {"page_url": "/movies/123"},
            },
        )
