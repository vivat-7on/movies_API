from typing import Protocol


class IEmailSender(Protocol):
    async def send(self, email: str, subject: str, body: str) -> None: ...
