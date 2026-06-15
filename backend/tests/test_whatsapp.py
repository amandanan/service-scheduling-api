import json

import pytest

import app.core.whatsapp as whatsapp


class _FakeResponse:
    def read(self):
        return b""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _capture_request(monkeypatch):
    captured = {}

    def _fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["method"] = request.get_method()
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return _FakeResponse()

    monkeypatch.setattr(whatsapp.urllib.request, "urlopen", _fake_urlopen)
    return captured


def test_zapi_request_shape(monkeypatch):
    monkeypatch.setenv("WHATSAPP_PROVIDER", "zapi")
    monkeypatch.setenv("WHATSAPP_API_URL", "https://api.z-api.io/instances/x/token/y/send-text")
    monkeypatch.setenv("WHATSAPP_CLIENT_TOKEN", "secret-token")

    captured = _capture_request(monkeypatch)

    whatsapp.send_whatsapp("(11) 97777-7777", "Olá")

    assert captured["method"] == "POST"
    assert captured["url"].endswith("/send-text")
    assert captured["body"] == {"phone": "5511977777777", "message": "Olá"}
    # urllib title-cases header names
    assert captured["headers"].get("Client-token") == "secret-token"


def test_evolution_request_shape(monkeypatch):
    monkeypatch.setenv("WHATSAPP_PROVIDER", "evolution")
    monkeypatch.setenv("WHATSAPP_API_URL", "https://evo.example.com/message/sendText/inst")
    monkeypatch.setenv("WHATSAPP_API_TOKEN", "evo-key")

    captured = _capture_request(monkeypatch)

    whatsapp.send_whatsapp("11977777777", "Oi")

    assert captured["body"] == {"number": "5511977777777", "text": "Oi"}
    assert captured["headers"].get("Apikey") == "evo-key"


def test_send_failure_raises(monkeypatch):
    """When the provider is configured but the HTTP call fails, send_whatsapp raises.

    NotificationService.deliver() catches the exception and logs "failed" so the
    booking is never broken, but send_whatsapp itself must not swallow errors.
    """
    monkeypatch.setenv("WHATSAPP_PROVIDER", "generic")
    monkeypatch.setenv("WHATSAPP_API_URL", "https://example.com/send")

    def _boom(request, timeout=None):
        raise OSError("network down")

    monkeypatch.setattr(whatsapp.urllib.request, "urlopen", _boom)

    with pytest.raises(OSError, match="network down"):
        whatsapp.send_whatsapp("11977777777", "Oi")
