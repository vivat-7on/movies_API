import datetime
import uuid

import pytest
from ugc_content_api.entities.ratings import MovieRating, MovieRatingSummary
from ugc_content_api.entities.reviews import (
    Review,
    ReviewDetails,
    ReviewSortOptions,
    ReviewSummary,
    ReviewVote,
)
from ugc_content_api.services.bookmarks import BookmarkService
from ugc_content_api.services.ratings import MovieRatingService
from ugc_content_api.services.reviews import ReviewService


class FakeBookmarkRepo:
    def __init__(self):
        self.bookmarks = []
        self.deleted_bookmarks = []

    async def get_user_bookmarks(self, user_id):
        return [bookmark for bookmark in self.bookmarks if bookmark.user_id == user_id]

    async def put_bookmark(self, bookmark):
        self.bookmarks.append(bookmark)

    async def delete_bookmark(self, user_id, movie_id):
        self.deleted_bookmarks.append((user_id, movie_id))


@pytest.fixture
def bookmarks_repo():
    return FakeBookmarkRepo()


@pytest.fixture
def bookmark_service(bookmarks_repo) -> BookmarkService:
    return BookmarkService(bookmarks_repo=bookmarks_repo)


class FakeMovieRatingRepo:
    def __init__(self):
        self.movie_ratings: list[MovieRating] = []
        self.deleted_movie_ratings = []

    async def get_summary(self, movie_id):
        return MovieRatingSummary(
            likes_count=0,
            dislikes_count=0,
            avg_score=None,
        )

    async def get_user_score(self, user_id, movie_id):
        for rating in self.movie_ratings:
            if rating.user_id == user_id and rating.movie_id == movie_id:
                return rating
        return None

    async def upsert_user_score(self, user_id, movie_id, score):
        now = datetime.datetime.now(datetime.timezone.utc)
        rating = MovieRating(
            movie_id=movie_id,
            user_id=user_id,
            score=score,
            created_at=now,
            updated_at=now,
        )
        self.movie_ratings.append(rating)
        return rating

    async def delete_user_score(self, user_id, movie_id):
        self.deleted_movie_ratings.append((user_id, movie_id))


@pytest.fixture
def movie_rating_repo():
    return FakeMovieRatingRepo()


@pytest.fixture
def movie_rating_service(movie_rating_repo) -> MovieRatingService:
    return MovieRatingService(repo=movie_rating_repo)


class FakeReviewRepo:
    def __init__(self):
        self.reviews: list[Review] = []
        self.deleted_reviews: list[uuid.UUID] = []
        self.updated_reviews: list[Review] = []

    async def get_review_by_id(self, review_id):
        review = [review for review in self.reviews if review.review_id == review_id]

        if not review:
            return None

        return review[0]

    async def create_review(self, review: Review) -> Review:
        self.reviews.append(review)
        return review

    async def update_review(self, review: Review) -> Review:
        self.updated_reviews.append(review)
        return review

    async def delete_review(self, review_id):
        self.deleted_reviews.append(review_id)
        self.reviews = [
            review for review in self.reviews if review.review_id != review_id
        ]

    async def get_review_details_by_movie_id(
        self,
        movie_id: uuid.UUID,
        page: int,
        page_size: int,
        sort: ReviewSortOptions | None = None,
    ) -> tuple[list[ReviewDetails], int]:
        matched_reviews = [
            review for review in self.reviews if review.movie_id == movie_id
        ]
        total = len(matched_reviews)
        if sort == ReviewSortOptions.created_at_asc:
            matched_reviews.sort(
                key=lambda review: (
                    review.created_at,
                    review.review_id,
                ),
            )
        else:
            matched_reviews.sort(
                key=lambda review: (
                    review.created_at,
                    review.review_id,
                ),
                reverse=True,
            )
        start = (page - 1) * page_size
        end = start + page_size
        page_reviews = matched_reviews[start:end]
        details = [
            ReviewDetails(
                review_id=review.review_id,
                user_id=review.user_id,
                movie_id=review.movie_id,
                title=review.title,
                text=review.text,
                likes=0,
                dislikes=0,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in page_reviews
        ]
        return details, total


@pytest.fixture
def review_repo():
    return FakeReviewRepo()


class FakeReviewVoteRepo:
    def __init__(self):
        self.votes: list[ReviewVote] = []
        self.deleted_votes = []

    async def upsert_vote(
        self,
        review_id,
        user_id,
        score,
    ):
        now = datetime.datetime.now(datetime.timezone.utc)
        vote = ReviewVote(
            review_id=review_id,
            user_id=user_id,
            score=score,
            created_at=now,
            updated_at=now,
        )
        self.votes.append(vote)

    async def delete_vote(self, review_id, user_id):
        self.deleted_votes.append((review_id, user_id))

    async def get_votes_summary(self, review_id) -> ReviewSummary:
        return ReviewSummary(
            review_id=review_id,
            likes=0,
            dislikes=0,
            avg_score=0.0,
        )

    async def get_vote(self, review_id, user_id):
        vote = [
            vote
            for vote in self.votes
            if vote.review_id == review_id and vote.user_id == user_id
        ]
        if not vote:
            return None

        return vote[0]


@pytest.fixture
def vote_repo():
    return FakeReviewVoteRepo()


@pytest.fixture
def review_service(
    review_repo,
    vote_repo,
) -> ReviewService:
    return ReviewService(
        review_repo=review_repo,
        vote_repo=vote_repo,
    )
