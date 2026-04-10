import uuid

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
        encoded_jwt = jwt.encode(
            claims=claim.model_dump(),
            key=self.auth_settings.JWT_SECRET_KEY,
            algorithm=self.auth_settings.JWT_ALGORITHM,
        )
        return encoded_jwt

    def generate_refresh_token(self) -> str:
        return uuid.uuid4().hex
