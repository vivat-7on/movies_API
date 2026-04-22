import secrets
import uuid
from datetime import datetime, timedelta, timezone

from attrs import frozen
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError

from auth.core.config import AuthSettings
from auth.dtos.token import ClaimDTO
from auth.exceptions.auth import InvalidCredentials


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
        return secrets.token_urlsafe(32)

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

    def decode_access_token(
        self,
        access_token: str,
    ) -> ClaimDTO:
        try:
            payload = jwt.decode(
                access_token,
                key=self.auth_settings.JWT_SECRET_KEY,
                algorithms=[self.auth_settings.JWT_ALGORITHM],
                options={
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
        except ExpiredSignatureError:
            raise InvalidCredentials("Token expired") from None

        except JWTError:
            raise InvalidCredentials("Token invalid") from None

        try:
            claim = ClaimDTO(**payload)
        except ValidationError as exc:
            raise InvalidCredentials("Invalid token pyload") from exc

        return claim
