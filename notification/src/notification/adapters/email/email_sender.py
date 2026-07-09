import asyncio
import smtplib
from email.message import EmailMessage

from notification.core.email_settings import EmailSettings
from notification.interfaces.email_sender import IEmailSender


class EmailSender(IEmailSender):
    def __init__(self, email_settings: EmailSettings) -> None:
        self.email_settings = email_settings

    async def send(
        self,
        email: str,
        subject: str,
        body: str,
    ) -> None:
        await asyncio.to_thread(
            self._send_sync,
            email=email,
            subject=subject,
            body=body,
        )

    def _send_sync(
        self,
        email: str,
        subject: str,
        body: str,
    ) -> None:
        message = EmailMessage()
        message["From"] = self.email_settings.SMTP_FROM
        message["To"] = email
        message["Subject"] = subject
        message.set_content(body, subtype="html")

        with smtplib.SMTP_SSL(
            self.email_settings.SMTP_HOST,
            self.email_settings.SMTP_PORT,
        ) as smtp:
            smtp.login(
                self.email_settings.SMTP_USER,
                self.email_settings.SMTP_PASSWORD,
            )
            smtp.send_message(message)
