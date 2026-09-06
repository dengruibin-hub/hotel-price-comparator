from dataclasses import dataclass

from models.schemas import CompareRequest, HotelPrice
from services.hotel_matcher import HotelCandidate, match_hotel


@dataclass
class SearchResult:
    hotel: HotelCandidate
    match_score: float
    matched_sources: list[str]
    prices: list[HotelPrice]


def search_and_compare(request: CompareRequest) -> SearchResult:
    """Run the MVP hotel matching flow before comparing normalized prices.

    Provider results are still simulated. The important part is that the
    comparison now has a canonical hotel identity and an explicit match score.
    """
    candidates = [
        HotelCandidate(
            source="qunar",
            source_hotel_id="qunar-demo-001",
            name=request.hotel_name,
            address="上海市黄浦区外滩附近",
            latitude=31.2400,
            longitude=121.4900,
            phone="021-60000000",
        ),
        HotelCandidate(
            source="zhixing",
            source_hotel_id="zhixing-demo-001",
            name=request.hotel_name,
            address="上海市黄浦区外滩附近",
            latitude=31.2402,
            longitude=121.4901,
            phone="021-60000000",
        ),
        HotelCandidate(
            source="amap",
            source_hotel_id="amap-demo-001",
            name=request.hotel_name,
            address="上海市黄浦区外滩附近",
            latitude=31.2399,
            longitude=121.4902,
            phone="021-60000000",
        ),
    ]

    matched = match_hotel(candidates)

    from providers.qunar.provider import QunarProvider
    from providers.zhixing.provider import ZhixingProvider
    from providers.amap.provider import AmapProvider

    prices = (
        QunarProvider().get_prices(request)
        + ZhixingProvider().get_prices(request)
        + AmapProvider().get_prices(request)
    )

    return SearchResult(
        hotel=matched.canonical_hotel,
        match_score=matched.match_score,
        matched_sources=sorted(candidate.source for candidate in matched.matched_candidates),
        prices=prices,
    )
