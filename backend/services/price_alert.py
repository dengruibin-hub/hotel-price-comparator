from __future__ import annotations

from datetime import datetime, timezone

from repositories.alert_repository import PriceAlert, PriceAlertRepository
from repositories.price_repository import PriceSnapshotRepository


def check_price_alerts(
    alerts: list[PriceAlert],
    price_repository: PriceSnapshotRepository,
) -> list[dict]:
    results: list[dict] = []
    for alert in alerts:
        if not alert.enabled:
            continue
        snapshots = price_repository.list_history(
            alert.hotel_id, alert.check_in, alert.check_out, alert.guests, alert.rooms
        )
        matching = [item.total_price for item in snapshots if item.currency == alert.currency]
        current_lowest = min(matching) if matching else None
        triggered = current_lowest is not None and current_lowest <= alert.target_price
        triggered_at = alert.triggered_at
        if triggered and triggered_at is None:
            triggered_at = datetime.now(timezone.utc)
        results.append({
            "alert_id": alert.id,
            "hotel_id": alert.hotel_id,
            "target_price": alert.target_price,
            "current_lowest": current_lowest,
            "triggered": triggered,
            "triggered_at": triggered_at,
        })
    return results


def check_and_update_alerts(
    alert_repository: PriceAlertRepository,
    price_repository: PriceSnapshotRepository,
) -> list[dict]:
    alerts = alert_repository.list_alerts()
    results = check_price_alerts(alerts, price_repository)
    for result in results:
        if result["triggered"]:
            alert = alert_repository.get(result["alert_id"])
            if alert and alert.triggered_at is None:
                alert_repository.update(alert.__class__(
                    id=alert.id,
                    hotel_id=alert.hotel_id,
                    check_in=alert.check_in,
                    check_out=alert.check_out,
                    guests=alert.guests,
                    rooms=alert.rooms,
                    target_price=alert.target_price,
                    currency=alert.currency,
                    enabled=alert.enabled,
                    created_at=alert.created_at,
                    triggered_at=result["triggered_at"],
                ))
    return results
