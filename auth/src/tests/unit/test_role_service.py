import uuid

import pytest
from auth.exceptions.role import RoleAlreadyExist, RoleNotFound

ROLE_NAME = "test_role"
ROLE_ID = uuid.UUID("28085bd5-ea61-4355-9526-1a5587e20bfd")


@pytest.mark.asyncio
async def test_create_role(role_service, role_repo):
    await role_service.create_role(ROLE_NAME)

    assert ROLE_NAME in role_repo.roles_by_name


@pytest.mark.asyncio
async def test_create_role_already_exists(role_service, role_repo):
    role_repo.roles_by_name[ROLE_NAME] = ROLE_ID

    with pytest.raises(RoleAlreadyExist):
        await role_service.create_role(ROLE_NAME)


@pytest.mark.asyncio
async def test_get_roles(role_service, role_repo):
    role_repo.roles_by_name[ROLE_NAME] = ROLE_ID
    roles = await role_service.get_roles()

    assert set(roles) == {ROLE_NAME}


@pytest.mark.asyncio
async def test_update_role(role_service, role_repo):
    role_repo.roles_by_name[ROLE_NAME] = ROLE_ID
    role_repo.roles_by_id[ROLE_ID] = ROLE_NAME

    await role_service.update_role(ROLE_ID, "new_role_name")

    assert role_repo.roles_by_name.get("new_role_name") == ROLE_ID
    assert ROLE_NAME not in role_repo.roles_by_name


@pytest.mark.asyncio
async def test_delete_role(role_service, role_repo):
    role_repo.roles_by_id[ROLE_ID] = ROLE_NAME
    role_repo.roles_by_name[ROLE_NAME] = ROLE_ID
    await role_service.delete_role(ROLE_ID)

    assert ROLE_ID not in role_repo.roles_by_id
    assert ROLE_NAME not in role_repo.roles_by_name


@pytest.mark.asyncio
async def test_update_role_not_found(role_service):
    with pytest.raises(RoleNotFound):
        await role_service.update_role(uuid.uuid4(), "new_name")


@pytest.mark.asyncio
async def test_update_role_name_already_exists(role_service, role_repo):
    admin_id = uuid.uuid4()
    role_repo.roles_by_name["admin"] = admin_id
    role_repo.roles_by_id[admin_id] = "admin"

    role_repo.roles_by_name["user"] = ROLE_ID
    role_repo.roles_by_id[ROLE_ID] = "user"

    with pytest.raises(RoleAlreadyExist):
        await role_service.update_role(ROLE_ID, "admin")


@pytest.mark.asyncio
async def test_delete_role_not_found(role_service):
    with pytest.raises(RoleNotFound):
        await role_service.delete_role(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_role_same_name_idempotent(role_service, role_repo):
    role_repo.roles_by_name[ROLE_NAME] = ROLE_ID
    role_repo.roles_by_id[ROLE_ID] = ROLE_NAME

    await role_service.update_role(ROLE_ID, ROLE_NAME)

    assert role_repo.roles_by_name[ROLE_NAME] == ROLE_ID
