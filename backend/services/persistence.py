from __future__ import annotations

from datetime import datetime, timezone

from models.hotel import HotelCandidate
from models.schemas import HotelPrice
from repositories.postgres_hotel_repository import PostgresHotelRepository
from repositories.postgres_price_repository import PostgresPriceSnapshotRepository
from repositories.price_repository import snapshot_from_price


def persist_comparison(
    hotel: HotelCandidate,
    candidates: list[HotelCandidate],
    match_score: float,
    prices: list[HotelPrice],
    check_in,
    check_out,
    guests: int,
    rooms: int,
) -> int:
    """Persist a successful comparison when PostgreSQL is configured."""
    hotel_repository = PostgresHotelRepository()
    price_repository = PostgresPriceSnapshotRepository()
    hotel_id = hotel_repository.upsert_hotel(hotel)

    for candidate in candidates:
        hotel_repository.upsert_source(hotel_id, candidate, match_score)

    checked_at = datetime.now(timezone.utc)
    for price in prices:
        price_repository.save_snapshot(
            snapshot_from_price(
                hotel_id=hotel_id,
                price=price,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                rooms=rooms,
                checked_at=checked_at,
            )
        )

    return hotel_id
