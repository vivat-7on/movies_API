import datetime
import uuid
from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class Review:
    review_id: uuid.UUID
    user_id: uuid.UUID
    movie_id: uuid.UUID
    title: str
    text: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ReviewVote:
    review_id: uuid.UUID
    user_id: uuid.UUID
    score: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ReviewDetails:
    review_id: uuid.UUID
    user_id: uuid.UUID
    movie_id: uuid.UUID
    title: str
    text: str
    likes: int
    dislikes: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ReviewSummary:
    review_id: uuid.UUID
    likes: int
    dislikes: int
    avg_score: float


class ReviewSortOptions(StrEnum):
    likes_desc = "likes"
    likes_asc = "-likes"
    title_desc = "title"
    title_asc = "-title"
