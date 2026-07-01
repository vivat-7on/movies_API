import datetime
import uuid
from typing import Any, Mapping, Sequence

from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.entities.ratings import MovieRating, MovieRatingSummary
from ugc_content_api.interfaces.ratings import IMovieRatingRepo


class MovieRatingRepo(IMovieRatingRepo):
    def __init__(self, db: AsyncDatabase) -> None:
        self.db = db

    async def get_summary(self, movie_id: uuid.UUID) -> MovieRatingSummary:
        pipeline: Sequence[Mapping[str, Any]] = [
            {"$match": {"movie_id": str(movie_id)}},
            {
                "$group": {
                    "_id": None,
                    "likes_count": {
                        "$sum": {"$cond": [{"$eq": ["$score", 10]}, 1, 0]},
                    },
                    "dislikes_count": {
                        "$sum": {"$cond": [{"$eq": ["$score", 0]}, 1, 0]},
                    },
                    "avg_score": {"$avg": "$score"},
                },
            },
        ]
        cursor = await self.db.movie_ratings.aggregate(pipeline=pipeline)
        docs = await cursor.to_list(length=None)
        if not docs:
            return MovieRatingSummary(
                likes_count=0,
                dislikes_count=0,
                avg_score=None,
            )
        doc = docs[0]
        return MovieRatingSummary(
            likes_count=doc["likes_count"],
            dislikes_count=doc["dislikes_count"],
            avg_score=doc["avg_score"],
        )

    async def get_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> MovieRating | None:
        score = await self.db.movie_ratings.find_one(
            {"movie_id": str(movie_id), "user_id": str(user_id)},
        )
        if score is None:
            return None

        return self._map_rating(score)

    async def upsert_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
        score: int,
    ) -> MovieRating:
        now = datetime.datetime.now(datetime.UTC)

        rating = await self.db.movie_ratings.find_one_and_update(
            {"movie_id": str(movie_id), "user_id": str(user_id)},
            {
                "$set": {
                    "score": score,
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "movie_id": str(movie_id),
                    "user_id": str(user_id),
                    "created_at": now,
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if rating is None:
            raise RuntimeError("Raiting was not updated")

        return self._map_rating(rating)

    async def delete_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None:
        await self.db.movie_ratings.delete_one(
            {"movie_id": str(movie_id), "user_id": str(user_id)},
        )

    @staticmethod
    def _map_rating(document: dict) -> MovieRating:
        return MovieRating(
            movie_id=uuid.UUID(document["movie_id"]),
            user_id=uuid.UUID(document["user_id"]),
            score=document["score"],
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )
