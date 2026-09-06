from __future__ import annotations

from datetime import date

from database import get_connection
from repositories.price_repository import PriceSnapshot


class PostgresPriceSnapshotRepository:
    """PostgreSQL implementation for persisted price snapshots."""

    def save_snapshot(self, snapshot: PriceSnapshot) -> None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO price_snapshots (
                        hotel_id, source, room_type, check_in, check_out,
                        guests, rooms, room_price, tax, fees, total_price,
                        currency, breakfast, cancelable, checked_at
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        snapshot.hotel_id,
                        snapshot.source,
                        snapshot.room_type,
                        snapshot.check_in,
                        snapshot.check_out,
                        snapshot.guests,
                        snapshot.rooms,
                        snapshot.room_price,
                        snapshot.tax,
                        snapshot.fees,
                        snapshot.total_price,
                        snapshot.currency,
                        snapshot.breakfast,
                        snapshot.cancelable,
                        snapshot.checked_at,
                    ),
                )
            connection.commit()

    def list_history(
        self,
        hotel_id: int,
        check_in: date,
        check_out: date,
        guests: int,
        rooms: int,
    ) -> list[PriceSnapshot]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT hotel_id, source, room_type, check_in, check_out,
                           guests, rooms, room_price, tax, fees, total_price,
                           currency, breakfast, cancelable, checked_at
                    FROM price_snapshots
                    WHERE hotel_id = %s
                      AND check_in = %s
                      AND check_out = %s
                      AND guests = %s
                      AND rooms = %s
                    ORDER BY checked_at DESC
                    """,
                    (hotel_id, check_in, check_out, guests, rooms),
                )
                rows = cursor.fetchall()

        return [PriceSnapshot(*row) for row in rows]
