from datetime import date, datetime, timezone

from models.schemas import HotelPrice
from repositories.price_repository import InMemoryPriceSnapshotRepository
from services.price_history import get_price_history, save_price_history


def test_save_price_history_persists_each_platform_snapshot():
    repository = InMemoryPriceSnapshotRepository()
    prices = [
        HotelPrice(
            source="qunar",
            room_name="高级大床房",
            price=598,
            currency="CNY",
            breakfast=True,
            cancelable=True,
        ),
        HotelPrice(
            source="zhixing",
            room_name="高级大床房",
            price=568,
            currency="CNY",
            breakfast=True,
            cancelable=True,
        ),
        HotelPrice(
            source="amap",
            room_name="高级大床房",
            price=620,
            currency="CNY",
            breakfast=True,
            cancelable=True,
        ),
    ]
    checked_at = datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc)

    count = save_price_history(
        repository,
        hotel_id=1,
        prices=prices,
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 12),
        guests=2,
        rooms=1,
        checked_at=checked_at,
    )

    assert count == 3
    history = get_price_history(
        repository,
        hotel_id=1,
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 12),
        guests=2,
        rooms=1,
    )

    assert len(history) == 3
    assert {item.source for item in history} == {"qunar", "zhixing", "amap"}
    assert {item.total_price for item in history} == {568, 598, 620}
    assert all(item.tax == 0 for item in history)
    assert all(item.fees == 0 for item in history)
    assert all(item.checked_at == checked_at for item in history)


def test_history_query_filters_by_booking_conditions():
    repository = InMemoryPriceSnapshotRepository()
    price = HotelPrice(
        source="qunar",
        room_name="高级大床房",
        price=598,
        currency="CNY",
        breakfast=True,
        cancelable=True,
    )

    save_price_history(
        repository,
        hotel_id=1,
        prices=[price],
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 12),
        guests=2,
        rooms=1,
    )

    assert get_price_history(
        repository,
        hotel_id=1,
        check_in=date(2026, 10, 11),
        check_out=date(2026, 10, 12),
        guests=2,
        rooms=1,
    ) == []
