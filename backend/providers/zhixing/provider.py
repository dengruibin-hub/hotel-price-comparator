from models.schemas import CompareRequest, HotelPrice
from providers.base import HotelProvider


class ZhixingProvider(HotelProvider):
    source = "zhixing"

    def get_prices(self, request: CompareRequest) -> list[HotelPrice]:
        return [
            HotelPrice(
                source=self.source,
                room_name="高级大床房",
                price=568,
                breakfast=True,
                cancelable=True,
            )
        ]
