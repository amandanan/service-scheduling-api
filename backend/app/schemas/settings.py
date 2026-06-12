from pydantic import BaseModel, ConfigDict, Field


class SettingsResponse(BaseModel):

    full_name: str
    booking_slug: str

    monthly_goal: float
    daily_capacity: int

    client_term_singular: str
    client_term_plural: str

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):

    monthly_goal: float = Field(ge=0)
    daily_capacity: int = Field(ge=1)

    client_term_singular: str = Field(min_length=1, max_length=40)
    client_term_plural: str = Field(min_length=1, max_length=40)
