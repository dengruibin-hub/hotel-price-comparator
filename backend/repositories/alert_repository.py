from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from typing import Protocol


@dataclass(frozen=True)
class PriceAlert:
    id: int
    hotel_id: int
    check_in: date
    check_out: date
    guests: int
    rooms: int
    target_price: float
    currency: str = "CNY"
    enabled: bool = True
    created_at: datetime = datetime.min.replace(tzinfo=timezone.utc)
    triggered_at: datetime | None = None


class PriceAlertRepository(Protocol):
    def create(self, alert: PriceAlert) -> PriceAlert: ...
    def list_alerts(self, hotel_id: int | None = None) -> list[PriceAlert]: ...
    def get(self, alert_id: int) -> PriceAlert | None: ...
    def update(self, alert: PriceAlert) -> PriceAlert: ...


class InMemoryPriceAlertRepository:
    def __init__(self) -> None:
        self._items: dict[int, PriceAlert] = {}
        self._next_id = 1

    def create(self, alert: PriceAlert) -> PriceAlert:
        item = replace(
            alert,
            id=self._next_id,
            created_at=alert.created_at if alert.created_at != datetime.min.replace(tzinfo=timezone.utc) else datetime.now(timezone.utc),
        )
        self._items[item.id] = item
        self._next_id += 1
        return item

    def list_alerts(self, hotel_id: int | None = None) -> list[PriceAlert]:
        items = list(self._items.values())
        if hotel_id is not None:
            items = [item for item in items if item.hotel_id == hotel_id]
        return sorted(items, key=lambda item: item.id)

    def get(self, alert_id: int) -> PriceAlert | None:
        return self._items.get(alert_id)

    def update(self, alert: PriceAlert) -> PriceAlert:
        if alert.id not in self._items:
            raise KeyError(f"Alert {alert.id} not found")
        self._items[alert.id] = alert
        return alert
