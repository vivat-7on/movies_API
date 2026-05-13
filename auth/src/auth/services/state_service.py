import secrets

from attr import frozen

from auth.exceptions.yandex_oauth import InvalidOAuthState
from auth.ports.cache.state import ICacheStateRepo

STATE_TTL_SECONDS = 300


@frozen
class OAuthStateService:
    cache: ICacheStateRepo

    async def create_state(self) -> str:
        state = secrets.token_urlsafe(32)
        key = self._build_state_key(state)
        await self.cache.set(key=key, value="1", ttl=STATE_TTL_SECONDS)
        return state

    async def validate_state(self, state: str) -> None:
        key = self._build_state_key(state)

        exists = await self.cache.get(key=key)
        if not exists:
            raise InvalidOAuthState()

        await self.cache.delete(key=key)

    @staticmethod
    def _build_state_key(state: str) -> str:
        return f"oauth_state:{state}"
