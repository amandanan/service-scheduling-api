from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    birth_date = Column(Date, nullable=False)

    cpf = Column(String, unique=True, nullable=False)

    phone = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)

    hashed_password = Column(String, nullable=False)

    # only account owners have a public booking page; staff members share it
    booking_slug = Column(String, unique=True, nullable=True, index=True)

    # NULL for account owners; for staff members it points at the owner whose
    # business (clients, agenda, services) they operate on.
    account_owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    # "owner" or "staff"
    role = Column(String, nullable=False, default="owner")

    # Business settings — let the product adapt to any kind of establishment.
    monthly_goal = Column(Float, nullable=False, default=10000.0)

    daily_capacity = Column(Integer, nullable=False, default=20)

    client_term_singular = Column(String, nullable=False, default="Cliente")

    client_term_plural = Column(String, nullable=False, default="Clientes")