from urllib.parse import urlencode

from attr import frozen

from auth.core.config import YandexOAuthSettings
from auth.core.enums import OAuthProviderName
from auth.dtos.token import OAuthUserInfoDTO
from auth.exceptions.oauth import OAuthTokenExchangeFailed, OAuthUserInfoFailed
from auth.ports.provider.oauth import IOAuthProvider
from auth.services.yandex_client import YandexClient


@frozen
class YandexOAuthProvider(IOAuthProvider):
    settings: YandexOAuthSettings
    client: YandexClient

    name = OAuthProviderName.YANDEX.value

    def get_authorize_url(self, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self.settings.YANDEX_CLIENT_ID,
            "redirect_uri": self.settings.YANDEX_REDIRECT_URI,
            "state": state,
        }
        return f"{self.settings.YANDEX_AUTHORIZE_URI}?{urlencode(params)}"

    async def get_user_info_by_code(self, code: str) -> OAuthUserInfoDTO:
        tokens = await self.client.exchange_code_for_token(code=code)
        if tokens is None:
            raise OAuthTokenExchangeFailed()

        access_token = tokens.access_token
        user_info = await self.client.get_user_info(access_token=access_token)

        if user_info is None:
            raise OAuthUserInfoFailed()

        return OAuthUserInfoDTO(
            social_id=user_info.id,
            login=user_info.login,
            email=user_info.default_email,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )
