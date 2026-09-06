from models.hotel import HotelCandidate


class InMemoryHotelRepository:
    """Small repository abstraction used until PostgreSQL is enabled."""

    def __init__(self) -> None:
        self._hotels: dict[str, HotelCandidate] = {}
        self._sources: dict[tuple[str, str], HotelCandidate] = {}

    def save_canonical(self, hotel: HotelCandidate) -> HotelCandidate:
        self._hotels[hotel.source_hotel_id] = hotel
        return hotel

    def save_source(self, canonical_id: str, candidate: HotelCandidate) -> None:
        self._sources[(canonical_id, candidate.source)] = candidate

    def get_source(self, canonical_id: str, source: str) -> HotelCandidate | None:
        return self._sources.get((canonical_id, source))
