import uuid
from datetime import datetime, timedelta, timezone

from attrs import frozen
from jose import jwt

from auth.core.config import AuthSettings
from auth.dtos.token import ClaimDTO


@frozen
class TokenService:
    auth_settings: AuthSettings

    def generate_access_token(
        self,
        claim: ClaimDTO,
    ) -> str:
        return jwt.encode(
            claims=claim.model_dump(),
            key=self.auth_settings.JWT_SECRET_KEY,
            algorithm=self.auth_settings.JWT_ALGORITHM,
        )

    def generate_refresh_token(self) -> str:
        return uuid.uuid4().hex

    def build_claim(
        self,
        user_id: uuid.UUID,
        roles: list[str],
        token_version: int,
    ) -> ClaimDTO:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(
            minutes=self.auth_settings.ACCESS_TOKEN_TTL_MINUTES,
        )
        return ClaimDTO(
            sub=str(user_id),
            roles=roles,
            token_version=token_version,
            iat=int(now.timestamp()),
            exp=int(expires.timestamp()),
        )
