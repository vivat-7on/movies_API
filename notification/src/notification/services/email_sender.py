from dataclasses import dataclass


@dataclass(frozen=True)
class EmailSender:
    async def send(
        self,
        email: str,
        subject: str,
        body: str,
    ) -> None:
        print(f"Sending email to {email}: {subject}\n{body}")
