import os
import json
import logging
import urllib.request

logger = logging.getLogger(__name__)

# Brazil. Used to complete local numbers that omit the country code.
DEFAULT_COUNTRY_CODE = "55"


def normalize_phone(raw: str) -> str:
    """Return the phone number as digits in international format.

    Strips the mask/symbols and prepends the Brazilian country code when the
    number looks local. Returns "" for empty input.
    """

    digits = "".join(char for char in (raw or "") if char.isdigit())

    if not digits:
        return ""

    # already international, e.g. 5511999999999
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

    # generic HTTP provider
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return headers, {"phone": phone, "message": message}


def send_whatsapp(to: str, message: str) -> None:
    """Send a WhatsApp text message through the configured provider.

    Mirrors send_email: if no provider URL is configured (WHATSAPP_API_URL),
    the message is logged instead of sent so the app keeps working in
    dev/test. Delivery failures are logged, not raised, so they never break
    the request that triggered the notification.
    """

    phone = normalize_phone(to)

    if not phone:
        return

    url = os.getenv("WHATSAPP_API_URL", "").strip()

    if not url:
        logger.info(
            "WhatsApp not sent (provider not configured): to=%s\n%s",
            phone, message,
        )
        return

    provider = os.getenv("WHATSAPP_PROVIDER", "generic").lower()
    headers, body = _build_request(provider, phone, message)

    data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")

    for key, value in headers.items():
        request.add_header(key, value)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()

    except Exception:
        logger.exception("Failed to send WhatsApp to %s", phone)
