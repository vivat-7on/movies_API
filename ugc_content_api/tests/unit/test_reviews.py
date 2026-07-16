import datetime
import uuid

import pytest
from ugc_content_api.entities.reviews import Review
from ugc_content_api.exceptions.reviews import (
    ReviewForbiddenError,
    ReviewNotFound,
)

REVIEW_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
MOVIE_ID = uuid.uuid4()
TITLE = "test_title"
TEXT = "test_text"
NOW = datetime.datetime.now(datetime.timezone.utc)

REVIEW = Review(
    review_id=REVIEW_ID,
    user_id=USER_ID,
    movie_id=MOVIE_ID,
    title=TITLE,
    text=TEXT,
    created_at=NOW,
    updated_at=NOW,
)


@pytest.mark.asyncio
async def test_get_review_details(review_service, review_repo, vote_repo):
    await review_repo.create_review(REVIEW)

    review_by_id = await review_service.get_review_details(REVIEW_ID)

    assert review_by_id.review_id == REVIEW_ID
    assert review_by_id.user_id == USER_ID
    assert review_by_id.movie_id == MOVIE_ID
    assert review_by_id.title == TITLE
    assert review_by_id.text == TEXT


@pytest.mark.asyncio
async def test_get_reviews_by_movie_id(review_service, review_repo):
    await review_repo.create_review(REVIEW)

    reviews, total = await review_service.get_reviews_by_movie_id(
        movie_id=MOVIE_ID,
        page=1,
        page_size=20,
    )

    assert total == 1
    assert len(reviews) == 1

    review = reviews[0]

    assert review.review_id == REVIEW_ID
    assert review.user_id == USER_ID
    assert review.movie_id == MOVIE_ID
    assert review.title == TITLE
    assert review.text == TEXT


@pytest.mark.asyncio
async def test_create_review(review_service, review_repo):
    review = await review_service.create_review(
        movie_id=MOVIE_ID,
        user_id=USER_ID,
        title=TITLE,
        text=TEXT,
    )

    created_review = review_repo.reviews[0]

    assert created_review.user_id == review.user_id
    assert created_review.movie_id == review.movie_id
    assert created_review.title == review.title
    assert created_review.text == review.text
    assert created_review.created_at == review.created_at
    assert created_review.updated_at == review.updated_at


@pytest.mark.asyncio
async def test_update_review(review_service, review_repo):
    await review_repo.create_review(REVIEW)

    review = await review_service.update_review(
        review_id=REVIEW_ID,
        user_id=USER_ID,
        title=TITLE,
        text=TEXT,
    )

    updated_review = review_repo.reviews[0]

    assert updated_review.review_id == review.review_id
    assert updated_review.user_id == review.user_id
    assert updated_review.title == review.title
    assert updated_review.text == review.text


@pytest.mark.asyncio
async def test_delete_review(review_service, review_repo):
    await review_repo.create_review(REVIEW)

    await review_service.delete_review(
        review_id=REVIEW_ID,
        user_id=USER_ID,
    )

    deleted_review_id = review_repo.deleted_reviews[0]

    assert deleted_review_id == REVIEW_ID
    assert await review_repo.get_review_by_id(REVIEW_ID) is None


@pytest.mark.asyncio
async def test_upsert_vote(review_service, vote_repo, review_repo):
    await review_repo.create_review(REVIEW)

    await review_service.upsert_vote(
        review_id=REVIEW_ID,
        user_id=USER_ID,
        score=10,
    )

    vote = vote_repo.votes[0]

    assert vote.review_id == REVIEW_ID
    assert vote.user_id == USER_ID
    assert vote.score == 10


@pytest.mark.asyncio
async def test_delete_vote(review_service, vote_repo):
    await vote_repo.upsert_vote(
        review_id=REVIEW_ID,
        user_id=USER_ID,
        score=10,
    )

    await review_service.delete_vote(
        review_id=REVIEW_ID,
        user_id=USER_ID,
    )

    deleted_vote = vote_repo.deleted_votes[0]

    assert REVIEW_ID in deleted_vote
    assert USER_ID in deleted_vote


@pytest.mark.asyncio
async def test_update_review_forbidden(review_service, review_repo):
    await review_repo.create_review(REVIEW)

    with pytest.raises(ReviewForbiddenError):
        await review_service.update_review(
            review_id=REVIEW_ID,
            user_id=uuid.uuid4(),
            title=TITLE,
            text=TEXT,
        )


@pytest.mark.asyncio
async def test_get_review_details_not_found(review_service):
    with pytest.raises(ReviewNotFound):
        await review_service.get_review_details(uuid.uuid4())
