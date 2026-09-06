from datetime import date

from models.schemas import CompareRequest
from services.comparator import compare_prices


def test_compare_prices_returns_three_sources_and_lowest_price():
    request = CompareRequest(
        hotel_name="上海外滩某酒店",
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 12),
        guests=2,
        rooms=1,
    )

    result = compare_prices(request)

    assert len(result.prices) == 3
    assert {item.source for item in result.prices} == {"qunar", "zhixing", "amap"}
    assert result.lowest_price == 568
    assert result.lowest_source == "zhixing"
    assert result.highest_price == 620
    assert result.savings == 52
    assert result.canonical_hotel_id == "qunar-demo-001"
    assert result.matched_sources == ["amap", "qunar", "zhixing"]
    assert result.match_score >= 0.72
