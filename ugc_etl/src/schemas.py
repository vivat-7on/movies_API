from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EventTypes(StrEnum):
    click = "click"
    page_view = "page_view"
    video_quality_changed = "video_quality_changed"
    video_completed = "video_completed"
    search_filter_used = "search_filter_used"


class EventMessage(BaseModel):
    event_type: EventTypes
    user_id: UUID | None = None
    anonymous_id: str | None = None
    timestamp: datetime
    payload: dict[str, Any]
