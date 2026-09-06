from datetime import date

from services.comparator import compare_prices
from models.schemas import CompareRequest


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
