import datetime
import uuid
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class EventTypes(StrEnum):
    click = "click"
    page_view = "page_view"
    video_quality_changed = "video_quality_changed"
    video_completed = "video_completed"
    search_filter_used = "search_filter_used"


class EventIn(BaseModel):
    event_type: EventTypes
    anonymous_id: str | None = None
    timestamp: datetime.datetime
    payload: dict[str, Any]

    model_config = ConfigDict(extra="forbid")


class EventMessage(EventIn):
    user_id: uuid.UUID | None = None
