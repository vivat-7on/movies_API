import uuid
from typing import Protocol

from ugc_content_api.entities.ratings import MovieRating, MovieRatingSummary


class IMovieRatingRepo(Protocol):
    async def get_summary(self, movie_id: uuid.UUID) -> MovieRatingSummary: ...

    async def get_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> MovieRating | None: ...

    async def upsert_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
        score: int,
    ) -> MovieRating: ...

    async def delete_user_score(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None: ...
