from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):

    rating: int = Field(ge=1, le=5)

    comment: str | None = None


class ReviewResponse(BaseModel):

    id: int

    rating: int

    comment: str | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OwnerReviewResponse(ReviewResponse):

    client_name: str

    service_name: str

    scheduled_at: datetime


class ReviewSummary(BaseModel):

    average_rating: float | None

    total_reviews: int

    reviews: list[ReviewResponse]
