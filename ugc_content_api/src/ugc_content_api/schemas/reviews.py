import datetime
import uuid
from typing import Annotated

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    title: str
    text: str


class ReviewResponse(BaseModel):
    review_id: uuid.UUID
    title: str
    text: str
    likes: int | None = None
    dislikes: int | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ListReviewResponse(BaseModel):
    reviews: list[ReviewResponse]


class ReviewVoteRequest(BaseModel):
    score: Annotated[int, Field(ge=0, le=10)]
