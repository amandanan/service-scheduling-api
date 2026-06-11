from uuid import uuid4

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship

from app.database.session import Base


class Appointment(Base):

    __tablename__ = "appointments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id = Column(
        Integer,
        ForeignKey("clients.id")
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id")
    )

    professional_id = Column(
        Integer,
        ForeignKey("professionals.id"),
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    scheduled_at = Column(DateTime)

    # public token lets a client manage their own appointment without login
    public_token = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=lambda: uuid4().hex,
    )

    # "scheduled" or "cancelled"
    status = Column(
        String,
        nullable=False,
        default="scheduled",
    )


    client = relationship(
        "Client",
        back_populates="appointments"
    )

    service = relationship(
        "Service",
        back_populates="appointments"
    )
    