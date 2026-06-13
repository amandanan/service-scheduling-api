from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.session import Base


class Service(Base):

    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String)

    description = Column(String, nullable=True)

    price = Column(Float)

    duration_minutes = Column(
        Integer,
        default=60,
        nullable=False
    )

    is_active = Column(Boolean, default=True, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # null = account-wide service (managed by admin); set = owned by a
    # specific professional who manages it
    professional_id = Column(
        Integer,
        ForeignKey("professionals.id"),
        nullable=True,
    )

    appointments = relationship(
        "Appointment",
        back_populates="service"
    )