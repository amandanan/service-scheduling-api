from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
)

from app.database.session import Base


class Professional(Base):
    __tablename__ = "professionals"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
