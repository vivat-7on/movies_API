import uuid

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import UserRole
from auth.ports.db.user_role_repo import IUserRoleRepo


class UserRoleRepo(IUserRoleRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        stmt = (
            insert(UserRole)
            .values(user_id=user_id, role_id=role_id)
            .on_conflict_do_nothing(
                index_elements=["user_id", "role_id"],
            )
        )
        await self.session.execute(stmt)

    async def remove_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        stmt = (
            delete(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
        )
        await self.session.execute(stmt)
