import uuid
from datetime import datetime, timedelta, timezone

from attrs import frozen

from auth.core.config import AuthSettings
from auth.core.hashing import hash_password, hash_token, verify_password
from auth.dtos.token import TokensDTO
from auth.exceptions.auth import (
    EmailAlreadyExists,
    InvalidCredentials,
    LoginAlreadyExists,
)
from auth.exceptions.oauth import (
    LinkedOAuthUserNotFound,
)
from auth.exceptions.role import RoleNotFound
from auth.ports.db.refresh_token_repo import IRefreshTokenRepo
from auth.ports.db.roles_repo import IRoleRepo
from auth.ports.db.social_account_repo import ISocialAccountRepo
from auth.ports.db.user_repo import IUserRepo
from auth.ports.db.user_role_repo import IUserRoleRepo
from auth.services.oauth_resolver import OAuthProviderResolver
from auth.services.token_service import TokenService


@frozen
class AuthService:
    user_repo: IUserRepo
    refresh_token_repo: IRefreshTokenRepo
    token_service: TokenService
    auth_settings: AuthSettings
    role_repo: IRoleRepo
    user_role_repo: IUserRoleRepo
    social_account_repo: ISocialAccountRepo
    oauth_provider_resolver: OAuthProviderResolver

    async def login(
        self,
        login: str,
        password: str,
        user_agent: str | None = None,
    ) -> TokensDTO:
        user = await self.user_repo.get_by_login(login)
        if user is None:
            raise InvalidCredentials()

        if user.password_hash is None:
            raise InvalidCredentials()

        if not await verify_password(password, user.password_hash):
            raise InvalidCredentials()

        roles = await self.role_repo.get_by_user_id(user_id=user.id) or []

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
        user_by_login = await self.user_repo.get_by_login(login)
        if user_by_login:
            raise LoginAlreadyExists()

        if email and await self.user_repo.email_exists(email):
            raise EmailAlreadyExists()

        password_hash = await hash_password(password)

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

        roles = await self.role_repo.get_by_user_id(user_id=user.id) or []
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

    async def logout(self, refresh_token: str, user_id: str) -> None:
        refresh_token_hash = hash_token(refresh_token)
        token = await self.refresh_token_repo.get_by_hash(
            refresh_token_hash,
        )
        if token is None:
            return

        if str(token.user_id) != user_id:
            return

        await self.refresh_token_repo.delete(token)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise InvalidCredentials()
        await self.user_repo.increase_token_version(user_id=user.id)

    async def login_with_oauth_provider(
        self,
        provider_name: str,
        code: str,
        user_agent: str | None = None,
    ) -> TokensDTO:
        provider = self.oauth_provider_resolver.get_provider(
            provider_name=provider_name,
        )
        user_info = await provider.get_user_info_by_code(code=code)

        social = await self.social_account_repo.get_by_provider_and_social_id(
            social_id=user_info.social_id,
            provider=provider_name,
        )

        if social:
            user = await self.user_repo.get_by_id(social.user_id)
            if user is None:
                raise LinkedOAuthUserNotFound()
        else:
            if user_info.email and await self.user_repo.email_exists(
                email=user_info.email,
            ):
                raise EmailAlreadyExists()

            user = await self.user_repo.create(
                login=f"{provider_name}_{user_info.social_id}",
                password_hash=None,
                email=user_info.email,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
            )

            role_id = await self.role_repo.get_id_by_name(
                name=self.auth_settings.DEFAULT_ROLE_NAME,
            )

            if role_id is None:
                raise RoleNotFound()

            await self.user_role_repo.assign_role(
                role_id=role_id,
                user_id=user.id,
            )

            await self.social_account_repo.create(
                user_id=user.id,
                social_id=user_info.social_id,
                provider=provider_name,
            )

        roles = await self.role_repo.get_by_user_id(user_id=user.id) or []

        refresh_token = self.token_service.generate_refresh_token()

        now = datetime.now(tz=timezone.utc)
        refresh_token_expires_at = now + timedelta(
            days=self.auth_settings.REFRESH_TOKEN_TTL_DAYS,
        )

        await self.refresh_token_repo.save(
            refresh_token_hash=hash_token(refresh_token),
            user_id=user.id,
            expires_at=refresh_token_expires_at,
            user_agent=user_agent,
        )
        user_id = user.id
        token_version = user.token_version

        claim = self.token_service.build_claim(
            user_id=user_id,
            roles=roles,
            token_version=token_version,
        )

        access_token = self.token_service.generate_access_token(
            claim=claim,
        )

        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
