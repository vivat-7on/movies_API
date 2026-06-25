from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.core.connect import get_mongo_db
from ugc_content_api.repositories.ratings import MovieRatingRepo
from ugc_content_api.services.ratings import MovieRatingService


def create_movie_rating_repo(
    db: AsyncDatabase = Depends(get_mongo_db),
) -> MovieRatingRepo:
    return MovieRatingRepo(db=db)


def create_movie_rating_service(
    repo: MovieRatingRepo = Depends(create_movie_rating_repo),
) -> MovieRatingService:
    return MovieRatingService(repo=repo)
