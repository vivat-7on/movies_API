from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.core.connect import get_mongo_db
from ugc_content_api.repositories.ratings import MovieRatingRepo
from ugc_content_api.repositories.reviews import ReviewRepo, ReviewVoteRepo
from ugc_content_api.services.ratings import MovieRatingService
from ugc_content_api.services.reviews import ReviewService


def create_movie_rating_repo(
    db: AsyncDatabase = Depends(get_mongo_db),
) -> MovieRatingRepo:
    return MovieRatingRepo(db=db)


def create_review_repo(db: AsyncDatabase = Depends(get_mongo_db)) -> ReviewRepo:
    return ReviewRepo(db=db)


def create_vote_repo(
    db: AsyncDatabase = Depends(get_mongo_db),
) -> ReviewVoteRepo:
    return ReviewVoteRepo(db=db)


def create_movie_rating_service(
    repo: MovieRatingRepo = Depends(create_movie_rating_repo),
) -> MovieRatingService:
    return MovieRatingService(repo=repo)


def create_review_service(
    review_repo: ReviewRepo = Depends(create_review_repo),
    vote_repo: ReviewVoteRepo = Depends(create_vote_repo),
):
    return ReviewService(
        review_repo=review_repo,
        vote_repo=vote_repo,
    )
