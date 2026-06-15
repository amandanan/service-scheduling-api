from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app.database.session import Base


class NotificationLog(Base):
    """Audit trail of notification attempts (LGPD record of processing)."""

    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)

    # "email" | "whatsapp" | "-"
    channel = Column(String, nullable=False)

    # "confirmation" | "reminder"
    notification_type = Column(String, nullable=False)

    # "sent" | "skipped_no_consent" | "skipped_not_configured" | "failed"
    status = Column(String, nullable=False)

    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
