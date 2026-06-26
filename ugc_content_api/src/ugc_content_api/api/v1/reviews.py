import uuid

from fastapi import APIRouter, Depends, Query
from starlette import status

from ugc_content_api.api.v1.dependencies.auth import get_user_id
from ugc_content_api.api.v1.dependencies.services import (
    create_review_service,
)
from ugc_content_api.entities.reviews import ReviewSortOptions
from ugc_content_api.schemas.reviews import (
    ListReviewResponse,
    ReviewRequest,
    ReviewResponse,
    ReviewVoteRequest,
)
from ugc_content_api.services.reviews import ReviewService

movie_router = APIRouter(prefix="/movies", tags=["Reviews"])
review_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@movie_router.post(
    "/{movie_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie_review(
    movie_id: uuid.UUID,
    data: ReviewRequest,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ReviewService = Depends(create_review_service),
) -> ReviewResponse:
    review = await service.create_review(
        movie_id=movie_id,
        user_id=user_id,
        title=data.title,
        text=data.text,
    )

    return ReviewResponse(
        review_id=review.review_id,
        title=review.title,
        text=review.text,
        likes=0,
        dislikes=0,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@movie_router.get(
    "/{movie_id}/reviews",
    response_model=ListReviewResponse,
)
async def get_movie_review(
    movie_id: uuid.UUID,
    sort: ReviewSortOptions | None = Query(None),
    service: ReviewService = Depends(create_review_service),
) -> ListReviewResponse:
    reviews = await service.get_reviews_by_movie_id(
        movie_id=movie_id,
        sort=sort,
    )

    return ListReviewResponse(
        reviews=[
            ReviewResponse(
                review_id=review.review_id,
                title=review.title,
                text=review.text,
                likes=review.likes,
                dislikes=review.dislikes,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in reviews
        ],
    )


@review_router.get(
    "/{review_id}",
    response_model=ReviewResponse,
)
async def get_review(
    review_id: uuid.UUID,
    service: ReviewService = Depends(create_review_service),
) -> ReviewResponse:
    review = await service.get_review_details(review_id=review_id)
    return ReviewResponse(
        review_id=review.review_id,
        title=review.title,
        text=review.text,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@review_router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def update_review(
    review_id: uuid.UUID,
    data: ReviewRequest,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ReviewService = Depends(create_review_service),
) -> ReviewResponse:
    review = await service.update_review(
        review_id=review_id,
        user_id=user_id,
        title=data.title,
        text=data.text,
    )

    return ReviewResponse(
        review_id=review.review_id,
        title=review.title,
        text=review.text,
        likes=review.likes,
        dislikes=review.dislikes,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@review_router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ReviewService = Depends(create_review_service),
) -> None:
    await service.delete_review(review_id=review_id, user_id=user_id)


@review_router.put(
    "/{review_id}/votes/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def upsert_vote(
    review_id: uuid.UUID,
    data: ReviewVoteRequest,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ReviewService = Depends(create_review_service),
) -> None:
    await service.upsert_vote(
        review_id=review_id,
        user_id=user_id,
        score=data.score,
    )


@review_router.delete(
    "/{review_id}/votes/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vote(
    review_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ReviewService = Depends(create_review_service),
) -> None:
    await service.delete_vote(review_id=review_id, user_id=user_id)
