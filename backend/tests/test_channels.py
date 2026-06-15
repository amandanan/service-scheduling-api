"""Unit tests for the NotificationService fallback (priority-chain) behaviour.

All channel and DB interactions are mocked so these tests run with zero I/O
and exercise only the delivery logic in NotificationService.deliver().
"""

from unittest.mock import MagicMock

from app.core.notification_channel import Notification
from app.core.notifications import NotificationService


def _notification(**kwargs):
    defaults = dict(
        notification_type="confirmation",
        subject="Agendamento",
        body="Corpo",
        recipient_name="Cliente",
        recipient_phone="5511999999999",
        recipient_email="cliente@test.com",
        appointment_id=1,
    )
    return Notification(**{**defaults, **kwargs})


def _mock_channel(name, *, return_value=True, raises=None):
    ch = MagicMock()
    ch.name = name
    if raises is not None:
        ch.send.side_effect = raises
    else:
        ch.send.return_value = return_value
    return ch


def _consenting_client():
    c = MagicMock()
    c.notification_consent = True
    c.owner_id = 1
    c.id = 1
    return c


def _deliver(channels, notification=None, client=None):
    db = MagicMock()
    service = NotificationService(channels)
    service.deliver(
        db,
        client or _consenting_client(),
        notification or _notification(),
    )
    return db


class TestFallbackChain:
    def test_whatsapp_delivers_email_not_called(self):
        """First-channel success must stop the chain immediately."""
        wa = _mock_channel("whatsapp", return_value=True)
        em = _mock_channel("email", return_value=True)

        _deliver([wa, em])

        wa.send.assert_called_once()
        em.send.assert_not_called()

    def test_whatsapp_not_configured_falls_to_email(self):
        """False (not configured) from WhatsApp must try email."""
        wa = _mock_channel("whatsapp", return_value=False)
        em = _mock_channel("email", return_value=True)

        _deliver([wa, em])

        wa.send.assert_called_once()
        em.send.assert_called_once()

    def test_whatsapp_raises_falls_to_email(self):
        """An exception in WhatsApp must not abort the chain."""
        wa = _mock_channel("whatsapp", raises=RuntimeError("provider down"))
        em = _mock_channel("email", return_value=True)

        _deliver([wa, em])

        wa.send.assert_called_once()
        em.send.assert_called_once()

    def test_neither_configured_both_skipped(self):
        """Both channels returning False → chain exhausted, no delivery."""
        wa = _mock_channel("whatsapp", return_value=False)
        em = _mock_channel("email", return_value=False)

        _deliver([wa, em])

        wa.send.assert_called_once()
        em.send.assert_called_once()

    def test_no_consent_skips_all_channels(self):
        """Consent gate must prevent every channel from being tried."""
        wa = _mock_channel("whatsapp", return_value=True)
        em = _mock_channel("email", return_value=True)

        client = _consenting_client()
        client.notification_consent = False

        _deliver([wa, em], client=client)

        wa.send.assert_not_called()
        em.send.assert_not_called()


class TestLogStatus:
    """Verify the status values logged for each outcome."""

    def _collect_log_statuses(self, channels):
        db = MagicMock()
        service = NotificationService(channels)
        service.deliver(db, _consenting_client(), _notification())

        from app.models.notification_log import NotificationLog
        statuses = {}
        for c in db.add.call_args_list:
            log: NotificationLog = c[0][0]
            statuses[log.channel] = log.status
        return statuses

    def test_delivered_channel_logged_as_sent(self):
        wa = _mock_channel("whatsapp", return_value=True)
        statuses = self._collect_log_statuses([wa])
        assert statuses["whatsapp"] == "sent"

    def test_not_configured_logged_correctly(self):
        wa = _mock_channel("whatsapp", return_value=False)
        em = _mock_channel("email", return_value=True)
        statuses = self._collect_log_statuses([wa, em])
        assert statuses["whatsapp"] == "skipped_not_configured"
        assert statuses["email"] == "sent"

    def test_exception_logged_as_failed(self):
        wa = _mock_channel("whatsapp", raises=IOError("timeout"))
        em = _mock_channel("email", return_value=True)
        statuses = self._collect_log_statuses([wa, em])
        assert statuses["whatsapp"] == "failed"
        assert statuses["email"] == "sent"

    def test_both_not_configured_logged(self):
        wa = _mock_channel("whatsapp", return_value=False)
        em = _mock_channel("email", return_value=False)
        statuses = self._collect_log_statuses([wa, em])
        assert statuses["whatsapp"] == "skipped_not_configured"
        assert statuses["email"] == "skipped_not_configured"
