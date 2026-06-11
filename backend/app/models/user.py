from sqlalchemy import Column, Integer, String, Date

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

    booking_slug = Column(String, unique=True, nullable=False, index=True)