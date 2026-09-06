from datetime import date, datetime

from pydantic import BaseModel, Field


class PriceAlertCreate(BaseModel):
    hotel_id: int = Field(ge=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1)
    rooms: int = Field(ge=1)
    target_price: float = Field(ge=0)
    currency: str = "CNY"
    enabled: bool = True


class PriceAlertResponse(PriceAlertCreate):
    id: int
    created_at: datetime
    triggered_at: datetime | None = None


class PriceAlertCheckResult(BaseModel):
    alert_id: int
    hotel_id: int
    target_price: float
    current_lowest: float | None = None
    triggered: bool
    triggered_at: datetime | None = None
