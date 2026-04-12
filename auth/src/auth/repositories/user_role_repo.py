import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from auth.models.models import UserRole
from auth.ports.user_role_repo import IUserRoleRepo


class UserRoleRepo(IUserRoleRepo):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def assign_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
