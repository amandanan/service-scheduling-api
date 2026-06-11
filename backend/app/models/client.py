from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class Client(Base):
    __tablename__ = "clients"

    __table_args__ = (
        UniqueConstraint("owner_id", "cpf", name="uq_clients_owner_cpf"),
        UniqueConstraint("owner_id", "email", name="uq_clients_owner_email"),
    )

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String)
    birth_date = Column(Date)
    cpf = Column(String)
    phone = Column(String)
    email = Column(String)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    appointments = relationship(
        "Appointment",
        back_populates="client"
    )