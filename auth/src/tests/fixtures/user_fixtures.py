import pytest
from auth.models.models import User
from auth.services.user_service import UserService


class FakeUserRoleRepo:
    def __init__(self):
        self.user_roles = {}

    async def assign_role(self, user_id, role_id):
        self.user_roles[user_id] = role_id

    async def remove_role(self, user_id, role_id):
        if self.user_roles.get(user_id) == role_id:
            del self.user_roles[user_id]


class FakeUserRepo:
    def __init__(self):
        self.users = {}

    async def get_by_id(self, user_id) -> User | None:
        return self.users.get(user_id)


class FakeRoleRepo:
    def __init__(self):
        self.roles = {}

    async def get_by_id(self, role_id):
        return self.roles.get(role_id)

    async def get_id_by_name(self, name):
        return self.roles.get(name)


@pytest.fixture
def user_repo_for_user():
    return FakeUserRepo()


@pytest.fixture
def role_repo_for_user():
    return FakeRoleRepo()


@pytest.fixture
def user_role_repo_for_user():
    return FakeUserRoleRepo()


@pytest.fixture
def user_service(
    user_repo_for_user,
    role_repo_for_user,
    user_role_repo_for_user,
    token_service,
):
    return UserService(
        user_repo=user_repo_for_user,
        role_repo=role_repo_for_user,
        user_role_repo=user_role_repo_for_user,
        token_service=token_service,
    )
