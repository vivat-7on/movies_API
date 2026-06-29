import uuid
from typing import Protocol

from ugc_content_api.entities.bookmarks import Bookmark


class IBookmarksRepo(Protocol):
    async def get_user_bookmarks(self, user_id: uuid.UUID) -> list[Bookmark]: ...

    async def put_bookmark(self, bookmark: Bookmark) -> None: ...

    async def delete_bookmark(
        self,
        user_id: uuid.UUID,
        movie_id: uuid.UUID,
    ) -> None: ...
