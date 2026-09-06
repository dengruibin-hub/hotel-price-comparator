from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class HotelCandidate:
    """A hotel record returned by one booking platform."""

    source: str
    source_hotel_id: str
    name: str
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: str = ""


@dataclass(frozen=True)
class HotelMatchResult:
    """Result of comparing one hotel candidate with a canonical hotel."""

    matched: bool
    match_score: float
    reasons: tuple[str, ...]
