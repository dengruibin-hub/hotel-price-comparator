from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from repositories.price_repository import PriceSnapshot


SOURCES = ("qunar", "zhixing", "amap")


def build_price_trend(snapshots: list[PriceSnapshot], days: int = 30) -> dict:
    """Build a compact trend series and summary metrics from price snapshots."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = [item for item in snapshots if item.checked_at >= cutoff]
    recent.sort(key=lambda item: item.checked_at)

    by_time: dict[datetime, dict[str, float]] = defaultdict(dict)
    for item in recent:
        by_time[item.checked_at][item.source] = item.total_price

    points = []
    for checked_at, prices in by_time.items():
        available = [prices[source] for source in SOURCES if source in prices]
        points.append(
            {
                "checked_at": checked_at,
                "qunar": prices.get("qunar"),
                "zhixing": prices.get("zhixing"),
                "amap": prices.get("amap"),
                "lowest": min(available) if available else None,
            }
        )

    all_prices = [item.total_price for item in recent]
    current_lowest = points[-1]["lowest"] if points else None
    historical_lowest = min(all_prices) if all_prices else None
    historical_average = round(sum(all_prices) / len(all_prices), 2) if all_prices else None

    def change_from(value: float | None) -> float | None:
        if current_lowest is None or value is None:
            return None
        return round(current_lowest - value, 2)

    return {
        "days": days,
        "current_lowest": current_lowest,
        "historical_lowest": historical_lowest,
        "historical_average": historical_average,
        "change_from_lowest": change_from(historical_lowest),
        "change_from_average": change_from(historical_average),
        "points": points,
    }
