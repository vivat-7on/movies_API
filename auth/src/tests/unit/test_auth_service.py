import datetime
import uuid

import pytest
from auth.core.hashing import hash_token, verify_password
from auth.exceptions.auth import (
    EmailAlreadyExists,
    InvalidCredentials,
    LoginAlreadyExists,
)
from auth.exceptions.role import RoleNotFound
from auth.models.models import RefreshToken

USER_ID = uuid.UUID("5e866b18-f369-4448-85ac-e8941cbfa044")
LOGIN = "test_login"
PASSWORD = "correct_password"


@pytest.mark.asyncio
async def test_login_success(auth_service, refresh_token_repo):
    result = await auth_service.login(
        login=LOGIN,
        password=PASSWORD,
    )

    assert result.access_token == "access_token"
    assert refresh_token_repo.saved_data["user_id"] == USER_ID
    assert refresh_token_repo.saved_data["expires_at"] is not None
    assert refresh_token_repo.saved_data["refresh_token_hash"] is not None
    assert refresh_token_repo.deleted_token is None


@pytest.mark.asyncio
async def test_login_invalid_password(auth_service):
    with pytest.raises(InvalidCredentials):
        await auth_service.login(
            login=LOGIN,
            password="wrong_password",
        )


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, user_repo):
    with pytest.raises(InvalidCredentials):
        await auth_service.login(
            login="wrong_login",
            password=PASSWORD,
        )


@pytest.mark.asyncio
async def test_login_claim(auth_service, token_service, role_repo):
    role_repo.roles_by_id[USER_ID] = ["user"]

    await auth_service.login(
        login=LOGIN,
        password=PASSWORD,
    )

    assert token_service.last_claim_input["roles"] == ["user"]
    assert token_service.last_claim_input["user_id"] == USER_ID
    assert token_service.last_claim_input["token_version"] == 1


@pytest.mark.asyncio
async def test_login_roles_none(auth_service, role_repo):
    async def fake_roles(*args, **kwargs):
        return None

    role_repo.get_by_user_id = fake_roles
    result = await auth_service.login(
        login=LOGIN,
        password=PASSWORD,
    )

    assert result.access_token == "access_token"


@pytest.mark.asyncio
async def test_user_registration(
    auth_service,
    user_repo,
    user_role_repo,
    role_repo,
):
    login = "test_registration_login"
    password = PASSWORD
    email = "test_email"
    first_name = "test_first_name"
    last_name = "test_last_name"
    role_repo.roles_by_name["user"] = uuid.uuid4()
    await auth_service.user_registration(
        login=login,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )

    user = user_repo.user

    assert user.login == login
    assert verify_password(password, user.password_hash)
    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user_role_repo.assigned is True


@pytest.mark.asyncio
async def test_user_registration_login_exists(auth_service):
    with pytest.raises(LoginAlreadyExists):
        login = LOGIN
        password = PASSWORD
        email = "test_email"
        first_name = "test_first_name"
        last_name = "test_last_name"
        await auth_service.user_registration(
            login=login,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )


@pytest.mark.asyncio
async def test_user_registration_email_exists(auth_service):
    with pytest.raises(EmailAlreadyExists):
        login = "new_login"
        password = PASSWORD
        email = "existing_email"
        first_name = "test_first_name"
        last_name = "test_last_name"
        await auth_service.user_registration(
            login=login,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )


@pytest.mark.asyncio
async def test_user_registration_role_not_found(
    auth_service_no_role,
):
    with pytest.raises(RoleNotFound):
        login = "test_registration_login"
        password = PASSWORD
        email = "test_email"
        first_name = "test_first_name"
        last_name = "test_last_name"
        await auth_service_no_role.user_registration(
            login=login,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )


@pytest.mark.asyncio
async def test_user_registration_no_default_role(auth_service):
    with pytest.raises(RoleNotFound):
        login = "test_registration_login"
        password = PASSWORD
        email = "test_email"
        first_name = "test_first_name"
        last_name = "test_last_name"
        await auth_service.user_registration(
            login=login,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )


@pytest.mark.asyncio
async def test_refresh_access_token(auth_service, refresh_token_repo):
    token_row = "refresh_token"
    hashed_token = hash_token(token_row)
    refresh_token_repo.token = RefreshToken(
        user_id=USER_ID,
        token_hash=hashed_token,
        expires_at=datetime.datetime(2220, 10, 10).astimezone(
            datetime.timezone.utc,
        ),
    )
    tokens = await auth_service.refresh_access_token(token_row)
    assert tokens.access_token == "access_token"
    assert refresh_token_repo.saved_data["refresh_token_hash"] == hash_token(
        tokens.refresh_token,
    )
    assert refresh_token_repo.deleted_token.token_hash == hashed_token
    assert refresh_token_repo.deleted_token.user_id == USER_ID


@pytest.mark.asyncio
async def test_refresh_old_token(auth_service, refresh_token_repo):
    with pytest.raises(InvalidCredentials):
        await auth_service.refresh_access_token("old_refresh_token")


@pytest.mark.asyncio
async def test_refresh_token_expired(auth_service, refresh_token_repo):
    token_row = "refresh_token"
    hashed = hash_token(token_row)

    refresh_token_repo.token = RefreshToken(
        user_id=USER_ID,
        token_hash=hashed,
        expires_at=datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
    )

    with pytest.raises(InvalidCredentials):
        await auth_service.refresh_access_token(token_row)


@pytest.mark.asyncio
async def test_refresh_token_reuse(auth_service, refresh_token_repo):
    token_row = "refresh_token"
    hashed = hash_token(token_row)

    refresh_token = RefreshToken(
        user_id=USER_ID,
        token_hash=hashed,
        expires_at=datetime.datetime(2220, 1, 1, tzinfo=datetime.timezone.utc),
    )

    refresh_token_repo.token = refresh_token

    await auth_service.refresh_access_token(token_row)

    refresh_token_repo.token = None

    with pytest.raises(InvalidCredentials):
        await auth_service.refresh_access_token(token_row)


@pytest.mark.asyncio
async def test_refresh_user_deleted(
    auth_service,
    refresh_token_repo,
    user_repo,
):
    token_row = "refresh_token"
    hashed = hash_token(token_row)

    refresh_token_repo.token = RefreshToken(
        user_id=USER_ID,
        token_hash=hashed,
        expires_at=datetime.datetime(2220, 1, 1, tzinfo=datetime.timezone.utc),
    )

    async def fake_get_user(*args, **kwargs):
        return None

    user_repo.get_by_id = fake_get_user

    with pytest.raises(InvalidCredentials):
        await auth_service.refresh_access_token(token_row)


@pytest.mark.asyncio
async def test_logout_success(auth_service, refresh_token_repo):
    token_row = "refresh_token"
    hashed_token = hash_token(token_row)
    refresh_token = RefreshToken(
        user_id=USER_ID,
        token_hash=hashed_token,
        expires_at=datetime.datetime(2220, 10, 10).astimezone(
            datetime.timezone.utc,
        ),
    )
    assert refresh_token_repo.deleted_token is None
    refresh_token_repo.token = refresh_token
    await auth_service.logout(token_row, str(USER_ID))
    assert refresh_token_repo.deleted_token is not None
    assert refresh_token_repo.deleted_token.token_hash == hashed_token
    assert refresh_token_repo.deleted_token.user_id == USER_ID


@pytest.mark.asyncio
async def test_logout_idempotent(auth_service, refresh_token_repo):
    refresh_token_repo.token = None

    await auth_service.logout("random_token", str(USER_ID))


@pytest.mark.asyncio
async def test_logout_all_success(auth_service, user_repo):
    await auth_service.logout_all(USER_ID)
    assert user_repo.token_version_increased_for == USER_ID
