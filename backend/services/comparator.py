from models.schemas import CompareRequest, CompareResponse, HotelPrice
from services.persistence import persist_comparison
from services.search_service import search_and_compare


def compare_prices(request: CompareRequest) -> CompareResponse:
    result = search_and_compare(request)
    prices: list[HotelPrice] = result.prices

    if not prices:
        raise ValueError("No hotel prices returned")

    lowest = min(prices, key=lambda item: item.price)
    highest_price = max(item.price for item in prices)

    # Persistence is optional so the original MVP remains runnable without PostgreSQL.
    from database import DATABASE_URL

    if DATABASE_URL:
        persist_comparison(
            hotel=result.hotel,
            candidates=result.candidates,
            match_score=result.match_score,
            prices=prices,
            check_in=request.check_in,
            check_out=request.check_out,
            guests=request.guests,
            rooms=request.rooms,
        )

    return CompareResponse(
        hotel_name=result.hotel.name,
        canonical_hotel_id=result.hotel.source_hotel_id,
        matched_sources=result.matched_sources,
        match_score=result.match_score,
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
