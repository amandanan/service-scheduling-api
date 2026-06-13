from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app.database.session import Base


class TimeBlock(Base):
    """A one-off period when a professional is unavailable (day off, break)."""

    __tablename__ = "time_blocks"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    professional_id = Column(
        Integer,
        ForeignKey("professionals.id"),
        nullable=False,
    )

    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)

    reason = Column(String, nullable=True)
