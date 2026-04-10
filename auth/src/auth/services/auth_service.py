from datetime import datetime, timedelta, timezone

from attrs import frozen

from auth.core.config import AuthSettings
from auth.core.hashing import verify_password
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
        if not user:
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

        await self.refresh_token_repo.save_refresh_token(
            refresh_token=refresh_token,
            user_id=str(user.id),
            expires_at=refresh_expires_at.timestamp(),
            created_at=now,
            user_agent=user_agent,
        )

        return TokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
