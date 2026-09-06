from datetime import date
from pydantic import BaseModel, Field, model_validator


class CompareRequest(BaseModel):
    hotel_name: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(default=2, ge=1)
    rooms: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class HotelPrice(BaseModel):
    source: str
    room_name: str
    price: float = Field(ge=0)
    currency: str = "CNY"
    breakfast: bool = False
    cancelable: bool = False


class CompareResponse(BaseModel):
    hotel_name: str
    check_in: date
    check_out: date
    guests: int
    rooms: int
    prices: list[HotelPrice]
    lowest_price: float
    lowest_source: str
    highest_price: float
    savings: float
