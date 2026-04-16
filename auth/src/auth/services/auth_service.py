import uuid
from datetime import datetime, timedelta, timezone

from attrs import frozen
from sqlalchemy.ext.asyncio import AsyncSession

from auth.core.config import AuthSettings
from auth.core.hashing import hash_password, hash_token, verify_password
from auth.dtos.token import TokensDTO, UserDTO
from auth.exceptions.auth import InvalidCredentials, RoleNotFound, UserNotFound
from auth.ports.refresh_token_repo import IRefreshTokenRepo
from auth.ports.roles_repo import IRoleRepo
from auth.ports.user_repo import IUserRepo
from auth.ports.user_role_repo import IUserRoleRepo
from auth.services.token_service import TokenService


@frozen
class AuthService:
    user_repo: IUserRepo
    refresh_token_repo: IRefreshTokenRepo
    token_service: TokenService
    auth_settings: AuthSettings
    role_repo: IRoleRepo
    user_role_repo: IUserRoleRepo
    session: AsyncSession

    async def login(
        self,
        login: str,
        password: str,
        user_agent: str | None = None,
    ) -> TokensDTO:
        user = await self.user_repo.get_by_login(login)
        if user is None:
            raise InvalidCredentials()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentials()

        roles = await self.role_repo.get_by_user_id(user_id=user.id)

        claim = self.token_service.build_claim(
            user_id=user.id,
            roles=roles,
            token_version=user.token_version,
        )

        access_token = self.token_service.generate_access_token(claim)
        refresh_token = self.token_service.generate_refresh_token()

        now = datetime.now(timezone.utc)
        refresh_expires_at = now + timedelta(
            days=self.auth_settings.REFRESH_TOKEN_TTL_DAYS,
        )

        refresh_token_hash = hash_token(refresh_token)

        await self.refresh_token_repo.save(
            refresh_token_hash=refresh_token_hash,
            user_id=user.id,
            expires_at=refresh_expires_at,
            user_agent=user_agent,
        )

        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def user_registration(
        self,
        login: str,
        password: str,
        email: str | None,
        first_name: str | None,
        last_name: str | None,
    ) -> None:
        user = await self.user_repo.get_by_login(login)
        if user:
            raise InvalidCredentials()

        if email and await self.user_repo.email_exists(email):
            raise InvalidCredentials()

        password_hash = hash_password(password)

        user = await self.user_repo.create(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        role_id = await self.role_repo.get_id_by_name(
            name=self.auth_settings.DEFAULT_ROLE_NAME,
        )

        if role_id is None:
            raise RoleNotFound()

        await self.user_role_repo.assign_role(
            user_id=user.id,
            role_id=role_id,
        )

    async def refresh_access_token(
        self,
        refresh_token: str,
        user_agent: str | None = None,
    ) -> TokensDTO:
        refresh_token_hash = hash_token(refresh_token)
        token = await self.refresh_token_repo.get_by_hash(
            refresh_token_hash,
        )

        if token is None:
            raise InvalidCredentials()

        now = datetime.now(timezone.utc)

        if token.expires_at < now:
            raise InvalidCredentials()

        new_refresh_token = self.token_service.generate_refresh_token()
        expires_at = now + timedelta(
            days=self.auth_settings.REFRESH_TOKEN_TTL_DAYS,
        )

        new_hash = hash_token(new_refresh_token)

        await self.refresh_token_repo.delete(token)
        await self.refresh_token_repo.save(
            refresh_token_hash=new_hash,
            user_id=token.user_id,
            expires_at=expires_at,
            user_agent=user_agent,
        )
        token_user_id = token.user_id

        user = await self.user_repo.get_by_id(token_user_id)
        if user is None:
            raise InvalidCredentials()

        roles = await self.role_repo.get_by_user_id(user_id=user.id)
        claim = self.token_service.build_claim(
            user_id=user.id,
            roles=roles,
            token_version=user.token_version,
        )

        access_token = self.token_service.generate_access_token(claim)

        return TokensDTO(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def get_current_user(self, access_token: str) -> UserDTO:
        claim = self.token_service.decode_access_token(access_token)

        user = await self.user_repo.get_by_id(uuid.UUID(claim.sub))
        if user is None:
            raise UserNotFound()

        if user.token_version != claim.token_version:
            raise InvalidCredentials()

        return UserDTO(
            user_id=str(user.id),
            roles=claim.roles,
        )

    async def logout(self, refresh_token: str) -> None:
        refresh_token_hash = hash_token(refresh_token)
        token = await self.refresh_token_repo.get_by_hash(
            refresh_token_hash,
        )
        if token is None:
            raise InvalidCredentials()
        await self.refresh_token_repo.delete(token)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise InvalidCredentials()
        await self.user_repo.increase_token_version(user_id=user.id)
