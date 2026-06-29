import datetime
import uuid

from pydantic import BaseModel, Field


class BookmarkResponse(BaseModel):
    bookmark_id: uuid.UUID
    movie_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BookmarksResponse(BaseModel):
    bookmarks: list[BookmarkResponse] = Field(default_factory=list)
