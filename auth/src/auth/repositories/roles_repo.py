import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import Role, UserRole
from auth.ports.roles_repo import IRoleRepo


class RoleRepo(IRoleRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[str]:
        stmt = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_id_by_name(self, name: str) -> uuid.UUID | None:
        stmt = select(Role.id).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_role(self, role_name: str) -> None:
        role = Role(name=role_name)
        self.session.add(role)

    async def get_roles(self) -> list[str]:
        stmt = select(Role.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_role(self, role_id: uuid.UUID, role_name: str) -> None:
        stmt = update(Role).where(Role.id == role_id).values(name=role_name)
        await self.session.execute(stmt)

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)
