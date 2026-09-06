from models.schemas import CompareRequest, HotelPrice
from providers.base import HotelProvider


class QunarProvider(HotelProvider):
    source = "qunar"

    def get_prices(self, request: CompareRequest) -> list[HotelPrice]:
        return [
            HotelPrice(
                source=self.source,
                room_name="高级大床房",
                price=598,
                breakfast=True,
                cancelable=True,
            )
        ]
