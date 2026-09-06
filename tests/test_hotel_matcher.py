from models.hotel import HotelCandidate
from services.hotel_matcher import match_hotel
from services.normalizer import normalize_phone, normalize_text


def test_normalizer_handles_spacing_and_punctuation():
    assert normalize_text(" 上海外滩 某酒店（旗舰店） ") == "上海外滩某酒店旗舰店"
    assert normalize_phone("021-1234 5678") == "02112345678"


def test_same_hotel_matches_with_multiple_signals():
    canonical = HotelCandidate(
        source="canonical",
        source_hotel_id="hotel-1",
        name="上海外滩某酒店",
        address="上海市黄浦区中山东一路100号",
        latitude=31.2401,
        longitude=121.4902,
        phone="021-12345678",
    )
    candidate = HotelCandidate(
        source="qunar",
        source_hotel_id="q-99",
        name="上海外滩某酒店",
        address="上海市黄浦区中山东一路100号",
        latitude=31.2408,
        longitude=121.4905,
        phone="02112345678",
    )

    result = match_hotel(canonical, candidate)

    assert result.matched is True
    assert result.match_score >= 0.9


def test_same_name_different_address_is_not_enough():
    canonical = HotelCandidate("canonical", "hotel-1", "上海国际酒店", "黄浦区南京东路1号")
    candidate = HotelCandidate("amap", "a-2", "上海国际酒店", "浦东新区世纪大道88号")

    result = match_hotel(canonical, candidate)

    assert result.matched is False


def test_different_hotels_do_not_match():
    canonical = HotelCandidate("canonical", "hotel-1", "上海外滩某酒店", "黄浦区中山东一路100号", 31.2401, 121.4902)
    candidate = HotelCandidate("zhixing", "z-3", "上海浦东某酒店", "浦东新区世纪大道500号", 31.2200, 121.5500)

    result = match_hotel(canonical, candidate)

    assert result.matched is False
