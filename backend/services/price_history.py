from __future__ import annotations

from datetime import date, datetime, timezone

from models.schemas import HotelPrice
from repositories.price_repository import PriceSnapshotRepository, snapshot_from_price


def save_price_history(
    repository: PriceSnapshotRepository,
    hotel_id: int,
    prices: list[HotelPrice],
    check_in: date,
    check_out: date,
    guests: int,
    rooms: int,
    checked_at: datetime | None = None,
) -> int:
    """Persist one normalized price result as independent platform snapshots."""
    timestamp = checked_at or datetime.now(timezone.utc)
    count = 0

    for price in prices:
        repository.save_snapshot(
            snapshot_from_price(
                hotel_id=hotel_id,
                price=price,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                rooms=rooms,
                checked_at=timestamp,
            )
        )
        count += 1

    return count


def get_price_history(
    repository: PriceSnapshotRepository,
    hotel_id: int,
    check_in: date,
    check_out: date,
    guests: int,
    rooms: int,
):
    return repository.list_history(hotel_id, check_in, check_out, guests, rooms)
