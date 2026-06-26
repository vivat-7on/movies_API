import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from ugc_content_api.api.v1.dependencies.auth import get_user_id
from ugc_content_api.api.v1.dependencies.services import (
    create_movie_rating_service,
)
from ugc_content_api.schemas.ratings import (
    MovieRatingSummaryResponse,
    MyRatingResponse,
    RatingRequest,
)
from ugc_content_api.services.ratings import MovieRatingService

router = APIRouter(prefix="/movies", tags=["Ratings"])


@router.get(
    "/{movie_id}/ratings/summary",
    response_model=MovieRatingSummaryResponse,
)
async def get_rating_summary(
    movie_id: uuid.UUID,
    service: MovieRatingService = Depends(create_movie_rating_service),
) -> MovieRatingSummaryResponse:
    summary = await service.get_summary(movie_id=movie_id)
    return MovieRatingSummaryResponse(
        likes_count=summary.likes_count,
        dislikes_count=summary.dislikes_count,
        avg_score=summary.avg_score,
    )


@router.get("/{movie_id}/ratings/me", response_model=MyRatingResponse)
async def get_my_rating(
    movie_id: uuid.UUID,
    service: MovieRatingService = Depends(create_movie_rating_service),
    user_id: uuid.UUID = Depends(get_user_id),
) -> MyRatingResponse:
    score = await service.get_user_score(movie_id=movie_id, user_id=user_id)
    if score is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Rating not found",
        )
    return MyRatingResponse(
        score=score.score,
    )


@router.put(
    "/{movie_id}/ratings/me",
    response_model=MyRatingResponse,
    status_code=HTTPStatus.OK,
)
async def upsert_my_score(
    movie_id: uuid.UUID,
    data: RatingRequest,
    service: MovieRatingService = Depends(create_movie_rating_service),
    user_id: uuid.UUID = Depends(get_user_id),
) -> MyRatingResponse:
    score = await service.upsert_user_score(
        movie_id=movie_id,
        user_id=user_id,
        score=data.score,
    )
    return MyRatingResponse(
        score=score.score,
    )


@router.delete(
    "/{movie_id}/ratings/me",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_my_score(
    movie_id: uuid.UUID,
    service: MovieRatingService = Depends(create_movie_rating_service),
    user_id: uuid.UUID = Depends(get_user_id),
) -> None:
    await service.delete_user_score(movie_id=movie_id, user_id=user_id)
