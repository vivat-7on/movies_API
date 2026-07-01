import datetime
import uuid
from dataclasses import dataclass

from ugc_content_api.entities.bookmarks import Bookmark
from ugc_content_api.interfaces.bookmarks import IBookmarksRepo


@dataclass(frozen=True)
class BookmarkService:
    bookmarks_repo: IBookmarksRepo

    async def get_user_bookmarks(self, user_id: uuid.UUID) -> list[Bookmark]:
        return await self.bookmarks_repo.get_user_bookmarks(user_id)

    async def put_bookmark(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None:
        now = datetime.datetime.now(datetime.UTC)
        bookmark = Bookmark(
            bookmark_id=uuid.uuid4(),
            movie_id=movie_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await self.bookmarks_repo.put_bookmark(bookmark=bookmark)

    async def delete_bookmark(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None:
        await self.bookmarks_repo.delete_bookmark(
            user_id=user_id,
            movie_id=movie_id,
        )
