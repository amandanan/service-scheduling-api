from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.session import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id")
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id")
    )

    date = Column(DateTime)

    
    
    client = relationship(
        "Client",
        back_populates="appointments"
    )

    service = relationship(
        "Service",
        back_populates="appointments"
    )
    