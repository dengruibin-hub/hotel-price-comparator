from abc import ABC, abstractmethod

from models.schemas import CompareRequest, HotelPrice


class HotelProvider(ABC):
    source: str

    @abstractmethod
    def get_prices(self, request: CompareRequest) -> list[HotelPrice]:
        """Return normalized prices for one hotel search."""
        raise NotImplementedError
