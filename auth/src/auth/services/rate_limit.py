from attr import frozen

from auth.exceptions.rate_limit import TooManyRequests
from auth.ports.cache.rate_limit import IRateLimitRepo


@frozen
class RateLimitService:
    repo: IRateLimitRepo

    async def register_failed_login_attempt(self, ip: str, login: str) -> None:
        key = f"login_attempt:{ip}:{login}"
        attempts = await self.repo.increment_and_get(key, ttl=60)
        if attempts >= 5:
            raise TooManyRequests()

    async def check_registration_limit(self, ip: str) -> None:
        key = f"registration_attempt:{ip}"
        attempts = await self.repo.increment_and_get(key, ttl=3600)
        if attempts > 3:
            raise TooManyRequests()

    async def ensure_login_allowed(self, ip: str, login: str) -> None:
        key = f"login_attempt:{ip}:{login}"
        attempts = await self.repo.get(key=key)
        if attempts is not None and attempts >= 5:
            raise TooManyRequests()

    async def reset_login_attempts(self, ip: str, login: str) -> None:
        key = f"login_attempt:{ip}:{login}"
        await self.repo.delete(key=key)
