from typing import Annotated

from pydantic import BaseModel, Field


class MovieRatingSummaryResponse(BaseModel):
    likes_count: int
    dislikes_count: int
    avg_score: float | None = None


class MyRatingResponse(BaseModel):
    score: int


class RatingRequest(BaseModel):
    score: Annotated[int, Field(ge=0, le=10)]
