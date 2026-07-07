import datetime
import uuid

from pydantic import BaseModel, Field


class UserRegisteredEvent(BaseModel):
    user_id: uuid.UUID
    payload: dict = Field(default_factory=dict)


class BroadcastEvent(BaseModel):
    user_ids: list[uuid.UUID]
    template_code: str
    payload: dict = Field(default_factory=dict)


class NewMovieEvent(BaseModel):
    user_ids: list[uuid.UUID]
    movie_title: str


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    template_code: str
    status: str
    created_at: datetime.datetime
    last_error: str | None = None
    sent_at: datetime.datetime | None = None
