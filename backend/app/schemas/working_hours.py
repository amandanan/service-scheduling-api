from pydantic import BaseModel, ConfigDict, field_validator
from datetime import time


class WorkingHoursItem(BaseModel):
    weekday: int
    start_time: time
    end_time: time
    is_closed: bool = False

    @field_validator("weekday")
    @classmethod
    def validate_weekday(cls, value):
        if value < 0 or value > 6:
            raise ValueError("weekday must be between 0 (Monday) and 6 (Sunday)")
        return value


class WorkingHoursUpdate(BaseModel):
    days: list[WorkingHoursItem]


class WorkingHoursResponse(WorkingHoursItem):
    id: int

    model_config = ConfigDict(from_attributes=True)
