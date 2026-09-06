from datetime import date, datetime, timezone

from models.schemas import HotelPrice
from repositories.alert_repository import InMemoryPriceAlertRepository, PriceAlert
from repositories.price_repository import InMemoryPriceSnapshotRepository, snapshot_from_price
from services.price_alert import check_and_update_alerts


def test_price_alert_triggers_when_lowest_price_reaches_target():
    alerts = InMemoryPriceAlertRepository()
    prices = InMemoryPriceSnapshotRepository()
    alert = alerts.create(
        PriceAlert(
            id=0,
            hotel_id=1,
            check_in=date(2026, 10, 10),
            check_out=date(2026, 10, 12),
            guests=2,
            rooms=1,
            target_price=575,
            created_at=datetime.now(timezone.utc),
        )
    )

    for item in [
        HotelPrice(source="qunar", room_name="高级大床房", price=600),
        HotelPrice(source="zhixing", room_name="高级大床房", price=570),
        HotelPrice(source="amap", room_name="高级大床房", price=620),
    ]:
        prices.save_snapshot(
            snapshot_from_price(
                alert.hotel_id, item, alert.check_in, alert.check_out, 2, 1, datetime.now(timezone.utc)
            )
        )

    results = check_and_update_alerts(alerts, prices)

    assert results[0]["triggered"] is True
    assert results[0]["current_lowest"] == 570
    assert alerts.get(alert.id).triggered_at is not None
