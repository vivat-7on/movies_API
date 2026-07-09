import secrets

from fastapi import Header, HTTPException
from starlette import status

from notification.core.security_settings import SecuritySettings

security_settings = SecuritySettings()


async def verify_service_token(
    x_service_token: str | None = Header(default=None),
) -> None:
    if not x_service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing service token",
        )

    if not secrets.compare_digest(
        x_service_token,
        security_settings.NOTIFICATION_SERVICE_TOKEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Service token is invalid",
        )
