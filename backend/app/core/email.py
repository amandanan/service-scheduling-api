import os
import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text e-mail.

    Returns True  when the message is accepted by the SMTP server.
    Returns False when SMTP is not configured or ``to`` is empty
                  (logs the would-be message so dev/test runs stay observable).
    Raises        on SMTP connection / authentication / send failure so the
                  caller (NotificationChannel) can log the error and fall back.
    """

    host = os.getenv("SMTP_HOST")

    if not host or not to:
        logger.info(
            "Email not sent (SMTP not configured): to=%s subject=%r\n%s",
            to, subject, body,
        )
        return False

    message = EmailMessage()
    message["From"] = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or "no-reply@example.com"
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"

    with smtplib.SMTP(host, port) as server:
        if use_tls:
            server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(message)

    return True
