import uuid

from attr import frozen

from auth.exceptions.role import RoleNotFound
from auth.exceptions.user import UserNotFound
from auth.ports.roles_repo import IRoleRepo
from auth.ports.user_repo import IUserRepo
from auth.ports.user_role_repo import IUserRoleRepo


@frozen
class UserService:
    user_repo: IUserRepo
    role_repo: IRoleRepo
    user_role_repo: IUserRoleRepo

    async def assign_user_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        role = await self.role_repo.get_by_id(role_id)
        if role is None:
            raise RoleNotFound()

        await self.user_role_repo.assign_role(user_id, role_id)

    async def remove_user_role(
        self,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        await self.user_role_repo.remove_role(user_id, role_id)
