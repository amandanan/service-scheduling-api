import os
import json
import logging
import urllib.request

logger = logging.getLogger(__name__)

DEFAULT_COUNTRY_CODE = "55"


def normalize_phone(raw: str) -> str:
    """Return the phone number as digits in international format.

    Strips the mask/symbols and prepends the Brazilian country code when the
    number looks local. Returns "" for empty input.
    """

    digits = "".join(char for char in (raw or "") if char.isdigit())

    if not digits:
        return ""

    if digits.startswith(DEFAULT_COUNTRY_CODE) and len(digits) >= 12:
        return digits

    return DEFAULT_COUNTRY_CODE + digits


def _build_request(provider: str, phone: str, message: str):
    """Return (headers, body) shaped for the configured provider."""

    token = os.getenv("WHATSAPP_API_TOKEN", "")

    if provider == "evolution":
        headers = {"apikey": token} if token else {}
        return headers, {"number": phone, "text": message}

    if provider == "zapi":
        headers = {}
        client_token = os.getenv("WHATSAPP_CLIENT_TOKEN")
        if client_token:
            headers["Client-Token"] = client_token
        return headers, {"phone": phone, "message": message}

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return headers, {"phone": phone, "message": message}


def send_whatsapp(to: str, message: str) -> bool:
    """Send a WhatsApp text message through the configured provider.

    Returns True  when the provider accepted the message.
    Returns False when WHATSAPP_API_URL is not set or ``to`` is empty
                  (logs the would-be message so dev/test runs stay observable).
    Raises        on HTTP / provider errors so the caller (NotificationChannel)
                  can log the error and fall back to the next channel.
    """

    phone = normalize_phone(to)

    if not phone:
        return False

    url = os.getenv("WHATSAPP_API_URL", "").strip()

    if not url:
        logger.info(
            "WhatsApp not sent (provider not configured): to=%s\n%s",
            phone, message,
        )
        return False

    provider = os.getenv("WHATSAPP_PROVIDER", "generic").lower()
    headers, body = _build_request(provider, phone, message)

    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)

    with urllib.request.urlopen(request, timeout=10) as response:
        response.read()

    return True
