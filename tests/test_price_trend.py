from datetime import datetime, timedelta, timezone

from models.schemas import HotelPrice
from repositories.price_repository import InMemoryPriceSnapshotRepository, snapshot_from_price
from services.price_trend import build_price_trend


def test_build_price_trend_calculates_lowest_and_average():
    repository = InMemoryPriceSnapshotRepository()
    check_in = datetime(2026, 10, 10, tzinfo=timezone.utc).date()
    check_out = datetime(2026, 10, 12, tzinfo=timezone.utc).date()
    base = datetime.now(timezone.utc) - timedelta(days=2)

    first = [
        HotelPrice(source="qunar", room_name="高级大床房", price=600),
        HotelPrice(source="zhixing", room_name="高级大床房", price=580),
        HotelPrice(source="amap", room_name="高级大床房", price=620),
    ]
    second = [
        HotelPrice(source="qunar", room_name="高级大床房", price=590),
        HotelPrice(source="zhixing", room_name="高级大床房", price=570),
        HotelPrice(source="amap", room_name="高级大床房", price=610),
    ]

    for price in first:
        repository.save_snapshot(snapshot_from_price(1, price, check_in, check_out, 2, 1, base))
    for price in second:
        repository.save_snapshot(snapshot_from_price(1, price, check_in, check_out, 2, 1, base + timedelta(days=1)))

    trend = build_price_trend(repository.list_history(1, check_in, check_out, 2, 1), days=30)

    assert trend["current_lowest"] == 570
    assert trend["historical_lowest"] == 570
    assert trend["historical_average"] == 595
    assert len(trend["points"]) == 2
    assert trend["points"][0]["lowest"] == 580
    assert trend["points"][1]["lowest"] == 570
