import os
import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email.

    If SMTP is not configured (no SMTP_HOST), the email is logged
    instead of sent so the app keeps working in dev/test environments.
    Delivery failures are logged, not raised, so they never break the
    request that triggered the notification.
    """

    host = os.getenv("SMTP_HOST")

    if not host:
        logger.info(
            "Email not sent (SMTP not configured): to=%s subject=%r\n%s",
            to, subject, body,
        )
        return

    message = EmailMessage()
    message["From"] = os.getenv("SMTP_FROM") or os.getenv("SMTP_USER") or "no-reply@example.com"
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"

    try:
        with smtplib.SMTP(host, port) as server:
            if use_tls:
                server.starttls()

            if username and password:
                server.login(username, password)

            server.send_message(message)

    except Exception:
        logger.exception("Failed to send email to %s", to)
