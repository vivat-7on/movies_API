import datetime
import uuid

import pytest
from auth.api.v1.dependencies import get_current_user
from auth.core.hashing import hash_password
from auth.dtos.token import ClaimDTO, UserDTO
from auth.main import app
from auth.models.models import RefreshToken, User
from auth.services.auth_service import AuthService
from fastapi import HTTPException
from starlette import status
from starlette.testclient import TestClient

USER_ID = uuid.UUID("5e866b18-f369-4448-85ac-e8941cbfa044")


class FakeUserRepo:
    def __init__(self):
        self.user = None
        self.token_version_increased_for = None

    async def get_by_id(self, user_id) -> User | None:
        return User(
            id=USER_ID,
            login="test_login",
            password_hash=hash_password("correct_password"),
            token_version=1,
        )

    async def get_by_login(self, login: str) -> User | None:
        if login != "test_login":
            return None

        return User(
            id=USER_ID,
            login="test_login",
            password_hash=hash_password("correct_password"),
            token_version=1,
        )

    async def create(
        self,
        login: str,
        password_hash: str,
        email: str | None,
        first_name: str | None,
        last_name: str | None,
    ):
        user = User(
            id=USER_ID,
            login=login,
            password_hash=password_hash,
            token_version=1,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        self.user = user
        return user

    async def email_exists(self, email: str) -> bool:
        if email == "test_email":
            return False
        return True

    async def increase_token_version(self, user_id) -> None:
        self.token_version_increased_for = user_id


class FakeRoleRepo:
    async def get_by_user_id(self, user_id: uuid.UUID) -> list[str]:
        return ["user"]

    async def get_id_by_name(self, name: str) -> uuid.UUID | None:
        if name != "user":
            return None
        return uuid.uuid4()


class FakeRoleRepoNoRole:
    async def get_by_user_id(self, *_):
        return ["user"]

    async def get_id_by_name(self, name):
        return None


class FakeUserRoleRepo:
    def __init__(self):
        self.assigned = False

    async def assign_role(self, *args, **kwargs):
        self.assigned = True


class FakeClaim:
    def model_dump(self, *args, **kwargs):
        return FakeClaim()


class FakeTokenService:
    def __init__(self):
        self.last_claim_input = None

    def generate_access_token(self, claim) -> str:
        return "access_token"

    def generate_refresh_token(self, *args, **kwargs) -> str:
        return "new_refresh_token"

    def build_claim(
        self,
        user_id: uuid.UUID,
        roles: list[str] | None = None,
        token_version: int = 1,
    ):
        self.last_claim_input = {
            "user_id": user_id,
            "roles": roles,
            "token_version": token_version,
        }
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now + datetime.timedelta(days=10)
        return ClaimDTO(
            sub=str(user_id),
            roles=roles,
            token_version=token_version,
            iat=int(now.timestamp()),
            exp=int(exp.timestamp()),
        )


class FakeRefreshTokenRepo:
    def __init__(self, token=None):
        self.saved_data = None
        self.deleted_token = None
        self.token = token

    async def save(self, *args, **kwargs):
        self.saved_data = kwargs

    async def get_by_hash(self, *_):
        return self.token

    async def delete(self, token: RefreshToken) -> None:
        self.deleted_token = token


class FakeSession:
    class _Begin:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None

    def begin(self):
        return self._Begin()


class FakeAuthSettings:
    JWT_SECRET_KEY = "secret_key"
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_TTL_MINUTES = 1
    REFRESH_TOKEN_TTL_DAYS = 1
    DEFAULT_ROLE_NAME = "user"


def fake_get_current_user():
    return UserDTO(
        user_id="123",
        roles=["user"],
    )


def fake_get_admin():
    return UserDTO(
        user_id="123",
        roles=["admin"],
    )


def fake_invalid_user():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


@pytest.fixture
def user_repo():
    return FakeUserRepo()


@pytest.fixture
def refresh_token_repo():
    return FakeRefreshTokenRepo()


@pytest.fixture
def token_service():
    return FakeTokenService()


@pytest.fixture
def role_repo():
    return FakeRoleRepo()


@pytest.fixture
def session():
    return FakeSession()


@pytest.fixture
def auth_settings():
    return FakeAuthSettings()


@pytest.fixture
def user_role_repo():
    return FakeUserRoleRepo()


@pytest.fixture
def role_repo_no_role():
    return FakeRoleRepoNoRole()


@pytest.fixture
def auth_service(
    user_repo,
    refresh_token_repo,
    token_service,
    role_repo,
    session,
    auth_settings,
    user_role_repo,
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
        role_repo=role_repo,
        session=session,
        auth_settings=auth_settings,
        user_role_repo=user_role_repo,
    )


@pytest.fixture
def auth_service_no_role(
    user_repo,
    refresh_token_repo,
    token_service,
    session,
    auth_settings,
    user_role_repo,
    role_repo_no_role,
):
    return AuthService(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
        role_repo=role_repo_no_role,
        session=session,
        auth_settings=auth_settings,
        user_role_repo=user_role_repo,
    )


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_current_user():
    app.dependency_overrides[get_current_user] = fake_get_current_user
    yield


@pytest.fixture
def override_admin():
    app.dependency_overrides[get_current_user] = fake_get_admin
    yield


@pytest.fixture
def override_invalid_user():
    app.dependency_overrides[get_current_user] = fake_invalid_user
    yield
