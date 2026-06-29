import datetime
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    bookmark_id: uuid.UUID
    movie_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
