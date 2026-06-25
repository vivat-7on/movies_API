import uuid
from dataclasses import dataclass

from ugc_content_api.entities.ratings import MovieRating, MovieRatingSummary
from ugc_content_api.interfaces.ratings import IMovieRatingRepo


@dataclass(frozen=True)
class MovieRatingService:
    repo: IMovieRatingRepo

    async def get_summary(
        self,
        movie_id: uuid.UUID,
    ) -> MovieRatingSummary:
        return await self.repo.get_summary(movie_id=movie_id)

    async def get_user_score(
        self,
        movie_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> MovieRating | None:
        return await self.repo.get_user_score(
            movie_id=movie_id,
            user_id=user_id,
        )

    async def upsert_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
        score: int,
    ) -> MovieRating:
        return await self.repo.upsert_user_score(
            movie_id=movie_id,
            user_id=user_id,
            score=score,
        )

    async def delete_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None:
        return await self.repo.delete_user_score(
            movie_id=movie_id,
            user_id=user_id,
        )
