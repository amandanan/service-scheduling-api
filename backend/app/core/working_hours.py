from datetime import time

from sqlalchemy.orm import Session

from app.models.working_hours import WorkingHours


# weekday: (start, end, is_closed) -- 0 = Monday ... 6 = Sunday
DEFAULT_HOURS = {
    0: (time(8, 0), time(18, 0), False),
    1: (time(8, 0), time(18, 0), False),
    2: (time(8, 0), time(18, 0), False),
    3: (time(8, 0), time(18, 0), False),
    4: (time(8, 0), time(18, 0), False),
    5: (time(8, 0), time(12, 0), False),
    6: (time(8, 0), time(12, 0), True),
}


def get_or_create_working_hours(db: Session, owner_id: int):
    existing = {
        wh.weekday: wh
        for wh in db.query(WorkingHours).filter(
            WorkingHours.owner_id == owner_id
        ).all()
    }

    for weekday, (start, end, is_closed) in DEFAULT_HOURS.items():
        if weekday not in existing:
            new_entry = WorkingHours(
                owner_id=owner_id,
                weekday=weekday,
                start_time=start,
                end_time=end,
                is_closed=is_closed,
            )

            db.add(new_entry)
            existing[weekday] = new_entry

    db.commit()

    return [existing[weekday] for weekday in sorted(existing)]
