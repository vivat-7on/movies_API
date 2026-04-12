import uuid

from sqlalchemy import select
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
