import uuid

from fastapi import APIRouter, Depends
from starlette import status

from ugc_content_api.api.v1.dependencies.auth import get_user_id
from ugc_content_api.api.v1.dependencies.services import (
    create_bookmarks_service,
)
from ugc_content_api.schemas.bookmarks import (
    BookmarkResponse,
    BookmarksResponse,
)
from ugc_content_api.services.bookmarks import BookmarksService

movie_bookmarks_router = APIRouter(prefix="/movies", tags=["Bookmarks"])
bookmarks_router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@bookmarks_router.get("/me", response_model=BookmarksResponse)
async def bookmarks(
    user_id: uuid.UUID = Depends(get_user_id),
    service: BookmarksService = Depends(create_bookmarks_service),
) -> BookmarksResponse:
    bookmarks = await service.get_user_bookmarks(user_id)

    return BookmarksResponse(
        bookmarks=[
            BookmarkResponse(
                bookmark_id=bookmark.bookmark_id,
                movie_id=bookmark.movie_id,
                created_at=bookmark.created_at,
                updated_at=bookmark.updated_at,
            )
            for bookmark in bookmarks
        ],
    )


@movie_bookmarks_router.put(
    "/{movie_id}/bookmarks/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def put_bookmark_me(
    movie_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_id),
    service: BookmarksService = Depends(create_bookmarks_service),
) -> None:
    await service.put_bookmark(user_id=user_id, movie_id=movie_id)


@movie_bookmarks_router.delete(
    "/{movie_id}/bookmarks/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bookmark_me(
    movie_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_id),
    service: BookmarksService = Depends(create_bookmarks_service),
):
    await service.delete_bookmark(user_id=user_id, movie_id=movie_id)
