from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.session import Base


class Review(Base):

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id"),
        unique=True,
        nullable=False,
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    rating = Column(Integer, nullable=False)

    comment = Column(String, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    appointment = relationship("Appointment")

    @property
    def client_name(self) -> str:
        return self.appointment.client.full_name

    @property
    def service_name(self) -> str:
        return self.appointment.service.name

    @property
    def scheduled_at(self) -> datetime:
        return self.appointment.scheduled_at
