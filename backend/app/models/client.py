from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from app.database.session import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String)
    birth_date = Column(Date)
    cpf = Column(String, unique=True)
    phone = Column(String)
    email = Column(String, unique=True)

    
    appointments = relationship(
        "Appointment",
        back_populates="client"
    )