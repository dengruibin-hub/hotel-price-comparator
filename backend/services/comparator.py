from models.schemas import CompareRequest, CompareResponse, HotelPrice
from providers.amap.provider import AmapProvider
from providers.qunar.provider import QunarProvider
from providers.zhixing.provider import ZhixingProvider


PROVIDERS = [QunarProvider(), ZhixingProvider(), AmapProvider()]


def compare_prices(request: CompareRequest) -> CompareResponse:
    prices: list[HotelPrice] = []
    for provider in PROVIDERS:
        prices.extend(provider.get_prices(request))

    if not prices:
        raise ValueError("No hotel prices returned")

    lowest = min(prices, key=lambda item: item.price)
    highest_price = max(item.price for item in prices)

    return CompareResponse(
        hotel_name=request.hotel_name,
        check_in=request.check_in,
        check_out=request.check_out,
        guests=request.guests,
        rooms=request.rooms,
        prices=prices,
        lowest_price=lowest.price,
        lowest_source=lowest.source,
        highest_price=highest_price,
        savings=round(highest_price - lowest.price, 2),
    )
