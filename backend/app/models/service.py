from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
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

    price = Column(Float)

    duration_minutes = Column(
        Integer,
        default=60,
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    appointments = relationship(
        "Appointment",
        back_populates="service"
    )