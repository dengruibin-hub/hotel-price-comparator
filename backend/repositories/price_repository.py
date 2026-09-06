from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from models.schemas import HotelPrice


@dataclass(frozen=True)
class PriceSnapshot:
    hotel_id: int
    source: str
    room_type: str
    check_in: date
    check_out: date
    guests: int
    rooms: int
    room_price: float
    tax: float
    fees: float
    total_price: float
    currency: str
    breakfast: bool
    cancelable: bool
    checked_at: datetime


class PriceSnapshotRepository(Protocol):
    def save_snapshot(self, snapshot: PriceSnapshot) -> None:
        ...

    def list_history(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        guests: int,
        rooms: int,
    ) -> list[PriceSnapshot]:
        ...


class InMemoryPriceSnapshotRepository:
    """Test-friendly repository used before PostgreSQL persistence is enabled."""

    def __init__(self) -> None:
        self._snapshots: list[PriceSnapshot] = []

    def save_snapshot(self, snapshot: PriceSnapshot) -> None:
        self._snapshots.append(snapshot)

    def list_history(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        guests: int,
        rooms: int,
    ) -> list[PriceSnapshot]:
        return [
            item
            for item in self._snapshots
            if item.hotel_id == hotel_id
            and item.check_in == check_in
            and item.check_out == check_out
            and item.guests == guests
            and item.rooms == rooms
        ]


def snapshot_from_price(
    hotel_id: int,
    price: HotelPrice,
    check_in: date,
    check_out: date,
    guests: int,
    rooms: int,
    checked_at: datetime,
) -> PriceSnapshot:
    """Map the current normalized price model to the database snapshot shape.

    HotelPrice currently exposes one final price, so tax and fees are zero until
    providers expose those components separately.
    """
    return PriceSnapshot(
        hotel_id=hotel_id,
        source=price.source,
        room_type=price.room_name,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        rooms=rooms,
        room_price=price.price,
        tax=0.0,
        fees=0.0,
        total_price=price.price,
        currency=price.currency,
        breakfast=price.breakfast,
        cancelable=price.cancelable,
        checked_at=checked_at,
    )
