from models.schemas import CompareRequest, HotelPrice
from providers.base import HotelProvider


class AmapProvider(HotelProvider):
    source = "amap"

    def get_prices(self, request: CompareRequest) -> list[HotelPrice]:
        return [
            HotelPrice(
                source=self.source,
                room_name="高级大床房",
                price=620,
                breakfast=True,
                cancelable=True,
            )
        ]
