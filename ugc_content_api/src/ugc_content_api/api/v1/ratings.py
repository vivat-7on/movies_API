import uuid

from fastapi import APIRouter

router = APIRouter(prefix="/movies", tags=["Ratings"])


@router.get("/{movie_id}/ratings/summary")
async def get_rating_summary(
    movie_id: uuid.UUID,
):
    return movie_id


@router.get("/{movie_id}/ratings/me")
async def get_my_rating(
    movie_id: uuid.UUID,
):
    return movie_id


@router.put("/{movie_id}/ratings/me")
async def upsert_my_ratings(
    movie_id: uuid.UUID,
):
    return movie_id


@router.delete("/{movie_id}/ratings/me")
async def delete_my_ratings(
    movie_id: uuid.UUID,
):
    return movie_id
