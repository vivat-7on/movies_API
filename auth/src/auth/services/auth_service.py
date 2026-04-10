from datetime import datetime, timedelta, timezone

from attrs import frozen

from auth.core.config import AuthSettings
from auth.core.hashing import hash_password, hash_token, verify_password
from auth.dtos.token import ClaimDTO, TokensDTO
from auth.exceptions.auth import InvalidCredentials
from auth.ports.refresh_token_repo import IRefreshTokenRepo
from auth.ports.user_repo import IUserRepo
from auth.services.token_service import TokenService


@frozen
class AuthService:
    user_repo: IUserRepo
    refresh_token_repo: IRefreshTokenRepo
    token_service: TokenService
    auth_settings: AuthSettings

    async def login(
        self,
        login: str,
        password: str,
        user_agent: str | None = None,
    ) -> TokensDTO:
        user = await self.user_repo.get_user_by_login(login)
        if user is None:
            raise InvalidCredentials()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentials()

        now = datetime.now(timezone.utc)
        expires = now + timedelta(
            minutes=self.auth_settings.ACCESS_TOKEN_TTL_MINUTES,
        )

        claim = ClaimDTO(
            sub=str(user.id),
            roles=["roles"],
            token_version=user.token_version,
            iat=int(now.timestamp()),
            exp=int(expires.timestamp()),
        )

        access_token = self.token_service.generate_access_token(claim)
        refresh_token = self.token_service.generate_refresh_token()
        refresh_expires_at = now + timedelta(
            days=self.auth_settings.REFRESH_TOKEN_TTL_DAYS,
        )

        refresh_token_hash = hash_token(refresh_token)

        await self.refresh_token_repo.save_refresh_token(
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
        user = await self.user_repo.get_user_by_login(login)
        if user:
            raise InvalidCredentials()

        if email and await self.user_repo.email_exist(email):
            raise InvalidCredentials()

        password_hash = hash_password(password)

        await self.user_repo.create_user(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
