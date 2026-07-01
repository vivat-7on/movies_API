import uuid

import pytest


@pytest.mark.asyncio
async def test_get_user_bookmarks(bookmark_service):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()

    await bookmark_service.put_bookmark(user_id, movie_id)
    bookmark = await bookmark_service.get_user_bookmarks(user_id)

    assert len(bookmark) == 1
    assert bookmark[0].user_id == user_id
    assert bookmark[0].movie_id == movie_id


@pytest.mark.asyncio
async def test_put_bookmark(bookmark_service, bookmarks_repo):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()

    await bookmark_service.put_bookmark(user_id, movie_id)
    bookmark = bookmarks_repo.bookmarks
    assert bookmark[0].user_id == user_id
    assert bookmark[0].movie_id == movie_id
    assert bookmark[0].bookmark_id is not None
    assert bookmark[0].created_at is not None
    assert bookmark[0].updated_at is not None


@pytest.mark.asyncio
async def test_delete_bookmark(bookmark_service, bookmarks_repo):
    movie_id = uuid.uuid4()
    user_id = uuid.uuid4()
    await bookmark_service.delete_bookmark(user_id, movie_id)

    bookmark = bookmarks_repo.deleted_bookmarks
    del_user_id, del_movie_id = bookmark[0]
    assert del_user_id == user_id
    assert del_movie_id == movie_id
