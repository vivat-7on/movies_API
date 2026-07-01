import datetime
import uuid
from typing import Any, Mapping, Sequence

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.entities.reviews import (
    Review,
    ReviewSortOptions,
    ReviewSummary,
    ReviewVote,
)
from ugc_content_api.interfaces.reviews import IReviewRepo, IReviewVoteRepo

SORT_MAP = {
    ReviewSortOptions.created_at_asc: [("created_at", 1)],
    ReviewSortOptions.created_at_desc: [("created_at", -1)],
    ReviewSortOptions.title_asc: [("title", 1)],
    ReviewSortOptions.title_desc: [("title", -1)],
}


class ReviewRepo(IReviewRepo):
    def __init__(self, db: AsyncDatabase) -> None:
        self.db = db

    async def get_review_by_id(self, review_id: uuid.UUID) -> Review | None:
        review = await self.db.reviews.find_one({"review_id": str(review_id)})
        if review is None:
            return None
        return self._map_review(review)

    async def get_reviews_by_movie_id(
        self,
        movie_id: uuid.UUID,
        sort: ReviewSortOptions | None = None,
    ) -> list[Review]:
        cursor = self.db.reviews.find({"movie_id": str(movie_id)})

        if sort is not None:
            cursor = cursor.sort(SORT_MAP[sort])

        documents = await cursor.to_list(length=None)

        return [self._map_review(document) for document in documents]

    async def create_review(
        self,
        review: Review,
    ) -> Review:
        document = {
            "review_id": str(review.review_id),
            "user_id": str(review.user_id),
            "movie_id": str(review.movie_id),
            "title": review.title,
            "text": review.text,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
        }

        await self.db.reviews.insert_one(document)

        return review

    async def update_review(
        self,
        review: Review,
    ) -> Review:
        updated_review = await self.db.reviews.find_one_and_update(
            {"review_id": str(review.review_id)},
            {
                "$set": {
                    "title": review.title,
                    "text": review.text,
                    "updated_at": review.updated_at,
                },
            },
            return_document=ReturnDocument.AFTER,
        )
        if updated_review is None:
            raise RuntimeError("Review was not updated")

        return self._map_review(updated_review)

    async def delete_review(
        self,
        review_id: uuid.UUID,
    ) -> None:
        await self.db.reviews.delete_one({"review_id": str(review_id)})

    @staticmethod
    def _map_review(document: dict) -> Review:
        return Review(
            review_id=uuid.UUID(document["review_id"]),
            user_id=uuid.UUID(document["user_id"]),
            movie_id=uuid.UUID(document["movie_id"]),
            title=document["title"],
            text=document["text"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )


class ReviewVoteRepo(IReviewVoteRepo):
    def __init__(self, db: AsyncDatabase) -> None:
        self.db = db

    async def upsert_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        score: int,
    ) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)

        await self.db.review_votes.update_one(
            {"user_id": str(user_id), "review_id": str(review_id)},
            {
                "$set": {
                    "score": score,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "review_id": str(review_id),
                    "created_at": now,
                },
            },
            upsert=True,
        )

    async def delete_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        await self.db.review_votes.delete_one(
            {"review_id": str(review_id), "user_id": str(user_id)},
        )

    async def get_votes_summary(self, review_id: uuid.UUID) -> ReviewSummary:
        pipeline: Sequence[Mapping[str, Any]] = [
            {"$match": {"review_id": str(review_id)}},
            {
                "$group": {
                    "_id": None,
                    "likes": {
                        "$sum": {"$cond": [{"$eq": ["$score", 10]}, 1, 0]},
                    },
                    "dislikes": {
                        "$sum": {"$cond": [{"$eq": ["$score", 0]}, 1, 0]},
                    },
                    "avg_score": {"$avg": "$score"},
                },
            },
        ]
        cursor = await self.db.review_votes.aggregate(pipeline)
        docs = await cursor.to_list(length=None)
        if not docs:
            return ReviewSummary(
                review_id=review_id,
                likes=0,
                dislikes=0,
                avg_score=0,
            )

        doc = docs[0]
        return ReviewSummary(
            review_id=review_id,
            likes=doc["likes"],
            dislikes=doc["dislikes"],
            avg_score=doc["avg_score"],
        )

    async def get_vote(
        self,
        review_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ReviewVote | None:
        vote = await self.db.review_votes.find_one(
            {"review_id": str(review_id), "user_id": str(user_id)},
        )

        if vote is None:
            return None

        return ReviewVote(
            review_id=uuid.UUID(vote["review_id"]),
            user_id=uuid.UUID(vote["user_id"]),
            score=vote["score"],
            created_at=vote["created_at"],
            updated_at=vote["updated_at"],
        )
