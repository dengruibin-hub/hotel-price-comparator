from dataclasses import dataclass

from models.hotel import HotelCandidate
from models.schemas import CompareRequest, HotelPrice
from services.hotel_matcher import match_candidates


@dataclass
class SearchResult:
    hotel: HotelCandidate
    candidates: list[HotelCandidate]
    match_score: float
    matched_sources: list[str]
    prices: list[HotelPrice]


def search_and_compare(request: CompareRequest) -> SearchResult:
    """Run hotel matching before comparing normalized prices.

    Platform hotel records and prices are still simulated in this MVP.
    """
    candidates = [
        HotelCandidate("qunar", "qunar-demo-001", request.hotel_name, "上海市黄浦区外滩附近", 31.2400, 121.4900, "021-60000000"),
        HotelCandidate("zhixing", "zhixing-demo-001", request.hotel_name, "上海市黄浦区外滩附近", 31.2402, 121.4901, "021-60000000"),
        HotelCandidate("amap", "amap-demo-001", request.hotel_name, "上海市黄浦区外滩附近", 31.2399, 121.4902, "021-60000000"),
    ]

    canonical, match_score, matched_candidates = match_candidates(candidates)

    from providers.amap.provider import AmapProvider
    from providers.qunar.provider import QunarProvider
    from providers.zhixing.provider import ZhixingProvider

    prices = (
        QunarProvider().get_prices(request)
        + ZhixingProvider().get_prices(request)
        + AmapProvider().get_prices(request)
    )

    return SearchResult(
        hotel=canonical,
        candidates=candidates,
        match_score=match_score,
        matched_sources=sorted(candidate.source for candidate in matched_candidates),
        prices=prices,
    )
