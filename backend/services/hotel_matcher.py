from math import asin, cos, radians, sin, sqrt
from difflib import SequenceMatcher

from models.hotel import HotelCandidate, HotelMatchResult
from services.normalizer import normalize_phone, normalize_text


def _similarity(left: str, right: str) -> float:
    left = normalize_text(left)
    right = normalize_text(right)
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, left, right).ratio()


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return 2 * radius * asin(sqrt(a))


def match_hotel(canonical: HotelCandidate, candidate: HotelCandidate) -> HotelMatchResult:
    """Score whether two platform records represent the same physical hotel."""
    name_score = _similarity(canonical.name, candidate.name)
    address_score = _similarity(canonical.address, candidate.address)
    phone_equal = bool(normalize_phone(canonical.phone)) and normalize_phone(canonical.phone) == normalize_phone(candidate.phone)

    distance_km = None
    if None not in (canonical.latitude, canonical.longitude, candidate.latitude, candidate.longitude):
        distance_km = _distance_km(canonical.latitude, canonical.longitude, candidate.latitude, candidate.longitude)

    score = name_score * 0.55 + address_score * 0.25
    reasons: list[str] = []

    if name_score >= 0.9:
        reasons.append("hotel names are highly similar")
    elif name_score >= 0.75:
        reasons.append("hotel names are similar")

    if address_score >= 0.8:
        reasons.append("addresses are similar")

    if distance_km is not None:
        if distance_km <= 0.2:
            score += 0.15
            reasons.append("coordinates are within 200m")
        elif distance_km <= 1.0:
            score += 0.08
            reasons.append("coordinates are within 1km")

    if phone_equal:
        score += 0.05
        reasons.append("phone numbers match")

    has_secondary_signal = address_score >= 0.55 or phone_equal or (distance_km is not None and distance_km <= 1.0)
    matched = score >= 0.72 and has_secondary_signal

    return HotelMatchResult(matched=matched, match_score=round(min(score, 1.0), 4), reasons=tuple(reasons))


def match_candidates(candidates: list[HotelCandidate]) -> tuple[HotelCandidate, float, list[HotelCandidate]]:
    """Pick the first candidate as canonical and verify every other source against it."""
    if not candidates:
        raise ValueError("No hotel candidates returned")

    canonical = candidates[0]
    matched_candidates = [canonical]
    scores: list[float] = [1.0]

    for candidate in candidates[1:]:
        result = match_hotel(canonical, candidate)
        if result.matched:
            matched_candidates.append(candidate)
            scores.append(result.match_score)

    return canonical, round(min(scores), 4), matched_candidates
