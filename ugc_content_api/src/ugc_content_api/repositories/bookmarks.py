import uuid

from pymongo.asynchronous.database import AsyncDatabase

from ugc_content_api.entities.bookmarks import Bookmark
from ugc_content_api.interfaces.bookmarks import IBookmarksRepo


class BookmarksRepo(IBookmarksRepo):
    def __init__(self, db: AsyncDatabase) -> None:
        self.db = db

    async def get_user_bookmarks(self, user_id: uuid.UUID) -> list[Bookmark]:
        cursor = self.db.bookmarks.find({"user_id": str(user_id)})
        documents = await cursor.to_list(length=None)
        return [self._map_bookmark(doc) for doc in documents]

    async def put_bookmark(
        self,
        bookmark: Bookmark,
    ) -> None:
        await self.db.bookmarks.update_one(
            {
                "user_id": str(bookmark.user_id),
                "movie_id": str(bookmark.movie_id),
            },
            {
                "$set": {
                    "updated_at": bookmark.updated_at,
                },
                "$setOnInsert": {
                    "bookmark_id": str(bookmark.bookmark_id),
                    "user_id": str(bookmark.user_id),
                    "movie_id": str(bookmark.movie_id),
                    "created_at": bookmark.created_at,
                },
            },
            upsert=True,
        )

    async def delete_bookmark(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None:
        await self.db.bookmarks.delete_one(
            {
                "bookmark_id": str(user_id),
                "movie_id": str(movie_id),
            },
        )

    @staticmethod
    def _map_bookmark(document: dict) -> Bookmark:
        return Bookmark(
            bookmark_id=uuid.UUID(document["bookmark_id"]),
            movie_id=uuid.UUID(document["movie_id"]),
            user_id=uuid.UUID(document["user_id"]),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )
