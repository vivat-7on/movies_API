import uuid

from attr import frozen
from sqlalchemy.ext.asyncio import AsyncSession

from auth.exceptions.roles import RoleAlreadyExist, RoleNotFound
from auth.ports.roles_repo import IRoleRepo


@frozen
class RoleService:
    role_repo: IRoleRepo
    session: AsyncSession

    async def create_role(self, role_name: str) -> None:
        role_id = await self.role_repo.get_id_by_name(name=role_name)
        if role_id is not None:
            raise RoleAlreadyExist()
        await self.role_repo.create_role(role_name)

    async def get_roles(self) -> list[str]:
        return await self.role_repo.get_roles()

    async def update_role(self, role_id: uuid.UUID, role_name: str) -> None:
        role = await self.role_repo.get_by_id(role_id=role_id)
        if role is None:
            raise RoleNotFound()

        existing_id = await self.role_repo.get_id_by_name(name=role_name)
        if existing_id is not None and existing_id != role_id:
            raise RoleAlreadyExist()

        await self.role_repo.update_role(
            role_id=role_id,
            role_name=role_name,
        )
        await self.session.commit()

    async def delete_role(self, role_id: uuid.UUID) -> None:
        role = await self.role_repo.get_by_id(role_id=role_id)
        if role is None:
            raise RoleNotFound()

        await self.role_repo.delete(role=role)
