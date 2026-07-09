from unittest.mock import patch

import pytest
from notification.adapters.email.email_sender import EmailSender
from notification.core.email_settings import EmailSettings


@pytest.mark.asyncio
async def test_send_calls_sync_in_thread():
    sender = EmailSender(email_settings=EmailSettings())

    with patch.object(EmailSender, "_send_sync") as send_sync_mock:
        await sender.send(
            email="user@test.com",
            subject="test subject",
            body="<h1>Hello</h1>",
        )

    send_sync_mock.assert_called_once_with(
        email="user@test.com",
        subject="test subject",
        body="<h1>Hello</h1>",
    )


def test_send_sync_sends_email_via_smtp():
    settings = EmailSettings(
        SMTP_HOST="smtp.example.com",
        SMTP_PORT=465,
        SMTP_USER="user",
        SMTP_PASSWORD="password",
        SMTP_FROM="sender@test.com",
    )

    sender = EmailSender(email_settings=settings)

    with patch(
        "notification.adapters.email.email_sender.smtplib.SMTP_SSL",
    ) as smtp_cls:
        smtp = smtp_cls.return_value.__enter__.return_value

        sender._send_sync(
            email="user@test.com",
            subject="test subject",
            body="<h1>Hello</h1>",
        )

    smtp_cls.assert_called_once_with("smtp.example.com", 465)
    smtp.login.assert_called_once_with("user", "password")
    smtp.send_message.assert_called_once()

    message = smtp.send_message.call_args.args[0]

    assert message["To"] == "user@test.com"
    assert message["Subject"] == "test subject"
    assert message["From"] == "sender@test.com"
    assert message.get_content_subtype() == "html"
