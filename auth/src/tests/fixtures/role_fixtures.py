import uuid

import pytest
from auth.services.role_service import RoleService


class FakeRoleRepo:
    def __init__(self):
        self.roles_by_name = {}
        self.roles_by_id = {}
        self.created_roles = []

    async def get_by_user_id(self, user_id):
        return self.roles_by_id.get(user_id)

    async def get_id_by_name(self, name):
        return self.roles_by_name.get(name)

    async def create_role(self, role_name):
        role_id = uuid.uuid4()
        self.roles_by_name[role_name] = role_id
        self.roles_by_id[role_id] = role_name
        self.created_roles.append(role_name)

    async def get_roles(self):
        return list(self.roles_by_name.keys())

    async def get_by_id(self, role_id):
        name = self.roles_by_id.get(role_id)
        if name is None:
            return None
        return type("Role", (), {"id": role_id, "name": name})

    async def update_role(self, role_id, role_name):
        old_name = self.roles_by_id.get(role_id)
        if old_name:
            del self.roles_by_name[old_name]

        self.roles_by_name[role_name] = role_id
        self.roles_by_id[role_id] = role_name

    async def delete(self, role):
        role_id = role.id
        role_name = role.name
        self.roles_by_id.pop(role_id, None)
        self.roles_by_name.pop(role_name, None)


@pytest.fixture
def role_repo() -> FakeRoleRepo:
    return FakeRoleRepo()


@pytest.fixture
def role_service(
    role_repo,
) -> RoleService:
    return RoleService(role_repo=role_repo)
