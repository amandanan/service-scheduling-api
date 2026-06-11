from sqlalchemy import (
    Column,
    Integer,
    Time,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)

from app.database.session import Base


class WorkingHours(Base):
    __tablename__ = "working_hours"

    __table_args__ = (
        UniqueConstraint("owner_id", "weekday", name="uq_working_hours_owner_weekday"),
    )

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # 0 = Monday ... 6 = Sunday
    weekday = Column(Integer, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    is_closed = Column(Boolean, default=False, nullable=False)
