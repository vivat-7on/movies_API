import uuid
from typing import Protocol

from ugc_content_api.entities.reviews import (
    Review,
    ReviewSortOptions,
    ReviewSummary,
    ReviewVote,
)


class IReviewRepo(Protocol):
    async def get_review_by_id(self, review_id: uuid.UUID) -> Review | None: ...

    async def get_reviews_by_movie_id(
        self,
        movie_id: uuid.UUID,
        sort: ReviewSortOptions | None = None,
    ) -> list[Review]: ...

    async def create_review(
        self,
        review: Review,
    ) -> Review: ...

    async def update_review(
        self,
        review: Review,
    ) -> Review: ...

    async def delete_review(
        self,
        review_id: uuid.UUID,
    ) -> None: ...


class IReviewVoteRepo(Protocol):
    async def upsert_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        score: int,
    ) -> None: ...

    async def delete_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None: ...

    async def get_votes_summary(self, review_id: uuid.UUID) -> ReviewSummary: ...

    async def get_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ReviewVote | None: ...
