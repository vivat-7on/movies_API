import datetime
import uuid
from dataclasses import dataclass

from ugc_content_api.entities.reviews import (
    Review,
    ReviewDetails,
    ReviewSortOptions,
)
from ugc_content_api.exceptions.reviews import (
    ReviewForbiddenError,
    ReviewNotFound,
    VoteNotFound,
)
from ugc_content_api.interfaces.reviews import IReviewRepo, IReviewVoteRepo


@dataclass(frozen=True)
class ReviewService:
    review_repo: IReviewRepo
    vote_repo: IReviewVoteRepo

    async def get_review_details(self, review_id: uuid.UUID) -> ReviewDetails:
        review = await self.review_repo.get_review_by_id(review_id=review_id)
        if review is None:
            raise ReviewNotFound(f"Review {review_id} not found")

        review_vote = await self.vote_repo.get_votes_summary(
            review_id=review_id,
        )

        return ReviewDetails(
            review_id=review.review_id,
            user_id=review.user_id,
            movie_id=review.movie_id,
            title=review.title,
            text=review.text,
            likes=review_vote.likes,
            dislikes=review_vote.dislikes,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    async def get_reviews_by_movie_id(
        self,
        movie_id: uuid.UUID,
        sort: ReviewSortOptions | None = None,
    ) -> list[ReviewDetails]:
        reviews = await self.review_repo.get_reviews_by_movie_id(
            movie_id=movie_id,
            sort=sort,
        )

        reviews_details = []
        for review in reviews:
            review_details = await self.get_review_details(
                review_id=review.review_id,
            )
            reviews_details.append(review_details)

        return reviews_details

    async def create_review(
        self,
        movie_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        text: str,
    ) -> Review:
        now = datetime.datetime.now(datetime.timezone.utc)
        review = Review(
            review_id=uuid.uuid4(),
            user_id=user_id,
            movie_id=movie_id,
            title=title,
            text=text,
            created_at=now,
            updated_at=now,
        )
        return await self.review_repo.create_review(review=review)

    async def update_review(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        text: str,
    ) -> ReviewDetails:
        now = datetime.datetime.now(datetime.timezone.utc)

        review = await self.review_repo.get_review_by_id(review_id=review_id)

        if review is None:
            raise ReviewNotFound(f"Review {review_id} not found")

        if review.user_id != user_id:
            raise ReviewForbiddenError(
                f"You are not allowed to update review {review_id}",
            )

        new_review_obj = Review(
            review_id=review.review_id,
            user_id=user_id,
            movie_id=review.movie_id,
            title=title,
            text=text,
            created_at=review.created_at,
            updated_at=now,
        )

        new_review = await self.review_repo.update_review(review=new_review_obj)

        review_summary = await self.vote_repo.get_votes_summary(
            review_id=review_id,
        )

        return ReviewDetails(
            review_id=new_review.review_id,
            user_id=new_review.user_id,
            movie_id=new_review.movie_id,
            title=new_review.title,
            text=new_review.text,
            likes=review_summary.likes,
            dislikes=review_summary.dislikes,
            created_at=new_review.created_at,
            updated_at=new_review.updated_at,
        )

    async def delete_review(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        review = await self.review_repo.get_review_by_id(review_id=review_id)

        if review is None:
            raise ReviewNotFound(f"Review {review_id} not found")

        if review.user_id != user_id:
            raise ReviewForbiddenError("You are not allowed to delete review")

        await self.review_repo.delete_review(review_id=review_id)

    async def upsert_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        score: int,
    ) -> None:
        review = await self.review_repo.get_review_by_id(review_id=review_id)

        if review is None:
            raise ReviewNotFound(f"Review {review_id} not found")

        await self.vote_repo.upsert_vote(
            review_id=review_id,
            score=score,
            user_id=user_id,
        )

    async def delete_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        vote = await self.vote_repo.get_vote(
            review_id=review_id,
            user_id=user_id,
        )

        if vote is None:
            raise VoteNotFound(f"Vote {review_id} not found")

        await self.vote_repo.delete_vote(
            user_id=user_id,
            review_id=review_id,
        )
