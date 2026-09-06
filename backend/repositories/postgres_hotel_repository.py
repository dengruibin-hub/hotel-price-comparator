from __future__ import annotations

from models.hotel import HotelCandidate
from services.normalizer import normalize_phone, normalize_text
from database import get_connection


class PostgresHotelRepository:
    """Store canonical hotels and their platform-specific mappings."""

    def upsert_hotel(self, hotel: HotelCandidate) -> int:
        normalized_name = normalize_text(hotel.name)
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id FROM hotels
                    WHERE normalized_name = %s
                    ORDER BY id
                    LIMIT 1
                    """,
                    (normalized_name,),
                )
                row = cursor.fetchone()
                if row:
                    hotel_id = row[0]
                    cursor.execute(
                        """
                        UPDATE hotels SET name=%s, address=%s, latitude=%s,
                            longitude=%s, phone=%s, updated_at=NOW()
                        WHERE id=%s
                        """,
                        (hotel.name, hotel.address, hotel.latitude, hotel.longitude,
                         normalize_phone(hotel.phone), hotel_id),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO hotels
                            (name, normalized_name, address, latitude, longitude, phone)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (hotel.name, normalized_name, hotel.address, hotel.latitude,
                         hotel.longitude, normalize_phone(hotel.phone)),
                    )
                    hotel_id = cursor.fetchone()[0]
            connection.commit()
        return hotel_id

    def upsert_source(self, hotel_id: int, candidate: HotelCandidate, match_score: float) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO hotel_sources (
                        hotel_id, source, source_hotel_id, source_name,
                        source_address, source_latitude, source_longitude,
                        source_phone, match_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source, source_hotel_id) DO UPDATE SET
                        hotel_id=EXCLUDED.hotel_id,
                        source_name=EXCLUDED.source_name,
                        source_address=EXCLUDED.source_address,
                        source_latitude=EXCLUDED.source_latitude,
                        source_longitude=EXCLUDED.source_longitude,
                        source_phone=EXCLUDED.source_phone,
                        match_score=EXCLUDED.match_score,
                        updated_at=NOW()
                    """,
                    (hotel_id, candidate.source, candidate.source_hotel_id,
                     candidate.name, candidate.address, candidate.latitude,
                     candidate.longitude, normalize_phone(candidate.phone), match_score),
                )
            connection.commit()
