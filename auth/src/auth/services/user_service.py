import uuid

from attr import frozen

from auth.dtos.token import UserDTO
from auth.exceptions.auth import InvalidCredentials
from auth.exceptions.role import RoleNotFound
from auth.exceptions.user import UserNotFound
from auth.ports.roles_repo import IRoleRepo
from auth.ports.user_repo import IUserRepo
from auth.ports.user_role_repo import IUserRoleRepo
from auth.services.token_service import TokenService


@frozen
class UserService:
    user_repo: IUserRepo
    role_repo: IRoleRepo
    user_role_repo: IUserRoleRepo
    token_service: TokenService

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

        role = await self.role_repo.get_by_id(role_id)
        if role is None:
            raise RoleNotFound()

        await self.user_role_repo.remove_role(user_id, role_id)

    async def get_current_user(self, access_token: str) -> UserDTO:
        claim = self.token_service.decode_access_token(access_token)

        try:
            user_id = uuid.UUID(claim.sub)
        except ValueError as exc:
            raise InvalidCredentials() from exc

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        if user.token_version != claim.token_version:
            raise InvalidCredentials()

        return UserDTO(
            user_id=str(user.id),
            roles=claim.roles or [],
        )
