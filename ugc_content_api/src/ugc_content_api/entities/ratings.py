import datetime
import uuid
from dataclasses import dataclass


@dataclass
class MovieRating:
    movie_id: uuid.UUID
    user_id: uuid.UUID
    score: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class MovieRatingSummary:
    likes_count: int
    dislikes_count: int
    avg_score: float | None
