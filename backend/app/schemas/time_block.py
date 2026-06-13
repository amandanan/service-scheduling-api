from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class TimeBlockCreate(BaseModel):

    professional_id: int
    start_at: datetime
    end_at: datetime
    reason: str | None = None

    @model_validator(mode="after")
    def _check_range(self):
        if self.end_at <= self.start_at:
            raise ValueError("O fim do bloqueio deve ser depois do início")
        return self


class TimeBlockResponse(BaseModel):

    id: int
    professional_id: int
    start_at: datetime
    end_at: datetime
    reason: str | None

    model_config = ConfigDict(from_attributes=True)
