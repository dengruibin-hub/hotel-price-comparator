from datetime import date, datetime

from pydantic import BaseModel, Field


class PriceSnapshotCreate(BaseModel):
    hotel_id: int = Field(ge=1)
    source: str
    room_type: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1)
    rooms: int = Field(ge=1)
    room_price: float = Field(ge=0)
    tax: float = Field(default=0, ge=0)
    fees: float = Field(default=0, ge=0)
    total_price: float = Field(ge=0)
    currency: str = "CNY"
    breakfast: bool = False
    cancelable: bool = False
    checked_at: datetime | None = None


class PriceSnapshotResponse(PriceSnapshotCreate):
    id: int | None = None


class PriceHistoryResponse(BaseModel):
    hotel_id: int
    check_in: date
    check_out: date
    guests: int
    rooms: int
    snapshots: list[PriceSnapshotResponse]
