import uuid

import pytest
from auth.exceptions.auth import InvalidCredentials
from auth.exceptions.role import RoleNotFound
from auth.exceptions.user import UserNotFound
from auth.models.models import User

USER_ID = uuid.UUID("5e866b18-f369-4448-85ac-e8941cbfa044")
ROLE_ID = uuid.UUID("76e2c71a-a7f0-442e-8c74-f4834592b9bb")


@pytest.mark.asyncio
async def test_assign_user_role(
    user_service,
    user_repo_for_user,
    role_repo_for_user,
    user_role_repo_for_user,
):
    user = User(
        id=USER_ID,
        login="test",
        password_hash="hash",
        token_version=1,
    )
    user_repo_for_user.users[USER_ID] = user
    role_repo_for_user.roles[ROLE_ID] = "admin"

    await user_service.assign_user_role(USER_ID, ROLE_ID)

    assert user_role_repo_for_user.user_roles[USER_ID] == ROLE_ID


@pytest.mark.asyncio
async def test_assign_user_role_user_not_found(user_service):
    with pytest.raises(UserNotFound):
        await user_service.assign_user_role(uuid.uuid4(), ROLE_ID)


@pytest.mark.asyncio
async def test_assign_user_role_role_not_found(
    user_service,
    user_repo_for_user,
):
    user = User(
        id=USER_ID,
        login="test",
        password_hash="hash",
        token_version=1,
    )

    user_repo_for_user.users[USER_ID] = user

    with pytest.raises(RoleNotFound):
        await user_service.assign_user_role(USER_ID, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_current_user_token_version_mismatch(
    user_service,
    user_repo_for_user,
):
    class FakeClaim:
        sub = str(USER_ID)
        roles = ["user"]
        token_version = 1

    def fake_decode(*args, **kwargs):
        return FakeClaim()

    user_service.token_service.decode_access_token = fake_decode

    user = User(
        id=USER_ID,
        login="test",
        password_hash="hash",
        token_version=2,
    )

    user_repo_for_user.users[USER_ID] = user

    with pytest.raises(InvalidCredentials):
        await user_service.get_current_user("token")


@pytest.mark.asyncio
async def test_get_current_user_success(
    user_service,
    user_repo_for_user,
):
    class FakeClaim:
        sub = str(USER_ID)
        roles = ["user"]
        token_version = 1

    def fake_decode(*args, **kwargs):
        return FakeClaim()

    user_service.token_service.decode_access_token = fake_decode

    user = User(
        id=USER_ID,
        login="test",
        password_hash="hash",
        token_version=1,
    )

    user_repo_for_user.users[USER_ID] = user

    result = await user_service.get_current_user("token")

    assert result.user_id == str(USER_ID)
    assert result.roles == ["user"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_uuid(user_service):
    class FakeClaim:
        sub = "not-a-uuid"
        roles = ["user"]
        token_version = 1

    def fake_decode(*args, **kwargs):
        return FakeClaim()

    user_service.token_service.decode_access_token = fake_decode

    with pytest.raises(InvalidCredentials):
        await user_service.get_current_user("token")
