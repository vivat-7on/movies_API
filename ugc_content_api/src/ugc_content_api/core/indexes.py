from pymongo.asynchronous.database import AsyncDatabase


async def create_indexes(db: AsyncDatabase) -> None:
    await db.movie_ratings.create_index(
        [("movie_id", 1), ("user_id", 1)],
        unique=True,
    )
    await db.movie_ratings.create_index([("movie_id", 1), ("score", 1)])
    await db.movie_ratings.create_index([("user_id", 1)])

    await db.reviews.create_index(
        [("movie_id", 1), ("user_id", 1)],
        unique=True,
    )
    await db.reviews.create_index([("review_id", 1)], unique=True)
    await db.reviews.create_index([("movie_id", 1), ("created_at", -1)])
    await db.reviews.create_index([("movie_id", 1), ("title", 1)])

    await db.review_votes.create_index(
        [("review_id", 1), ("user_id", 1)],
        unique=True,
    )
    await db.review_votes.create_index([("review_id", 1), ("score", 1)])

    await db.bookmarks.create_index(
        [("user_id", 1), ("movie_id", 1)],
        unique=True,
    )
