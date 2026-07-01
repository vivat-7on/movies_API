import uuid

import pytest
from ugc_content_api.exceptions.ratings import ScoreNotFound


@pytest.mark.asyncio
async def test_get_summary(movie_rating_service):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()
    score = 10

    await movie_rating_service.upsert_user_score(user_id, movie_id, score)
    summary = await movie_rating_service.get_summary(movie_id)

    assert summary is not None
    assert summary.likes_count == 0
    assert summary.dislikes_count == 0
    assert summary.avg_score is None


@pytest.mark.asyncio
async def test_upsert_user_score(movie_rating_service):
    user_id = uuid.uuid4()
    movie_id = uuid.uuid4()
    score = 10

    rating = await movie_rating_service.upsert_user_score(
        user_id,
        movie_id,
        score,
    )

    assert rating is not None
    assert movie_id == rating.movie_id
    assert user_id == rating.user_id
    assert score == rating.score


@pytest.mark.asyncio
async def test_delete_user_score(movie_rating_service, movie_rating_repo):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()

    await movie_rating_service.upsert_user_score(user_id, movie_id, 10)

    await movie_rating_service.delete_user_score(user_id, movie_id)

    assert movie_rating_repo.deleted_movie_ratings == [(user_id, movie_id)]


@pytest.mark.asyncio
async def test_delete_user_score_not_found(movie_rating_service):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with pytest.raises(ScoreNotFound):
        await movie_rating_service.delete_user_score(user_id, movie_id)
