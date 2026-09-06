from __future__ import annotations

from datetime import date, datetime, timezone

from database import get_connection
from repositories.alert_repository import PriceAlert


class PostgresPriceAlertRepository:
    def create(self, alert: PriceAlert) -> PriceAlert:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO price_alerts
                        (hotel_id, check_in, check_out, guests, rooms, target_price, currency, enabled)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at, triggered_at
                    """,
                    (alert.hotel_id, alert.check_in, alert.check_out, alert.guests, alert.rooms,
                     alert.target_price, alert.currency, alert.enabled),
                )
                row = cursor.fetchone()
            connection.commit()
        return PriceAlert(
            id=row[0], hotel_id=alert.hotel_id, check_in=alert.check_in, check_out=alert.check_out,
            guests=alert.guests, rooms=alert.rooms, target_price=alert.target_price,
            currency=alert.currency, enabled=alert.enabled, created_at=row[1], triggered_at=row[2],
        )

    def list_alerts(self, hotel_id: int | None = None) -> list[PriceAlert]:
        query = """
            SELECT id, hotel_id, check_in, check_out, guests, rooms, target_price,
                   currency, enabled, created_at, triggered_at
            FROM price_alerts
        """
        params: tuple = ()
        if hotel_id is not None:
            query += " WHERE hotel_id = %s"
            params = (hotel_id,)
        query += " ORDER BY id"
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, alert_id: int) -> PriceAlert | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, hotel_id, check_in, check_out, guests, rooms, target_price,
                           currency, enabled, created_at, triggered_at
                    FROM price_alerts WHERE id = %s
                    """,
                    (alert_id,),
                )
                row = cursor.fetchone()
        return self._from_row(row) if row else None

    def update(self, alert: PriceAlert) -> PriceAlert:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE price_alerts
                    SET enabled = %s, triggered_at = %s
                    WHERE id = %s
                    RETURNING id, hotel_id, check_in, check_out, guests, rooms, target_price,
                              currency, enabled, created_at, triggered_at
                    """,
                    (alert.enabled, alert.triggered_at, alert.id),
                )
                row = cursor.fetchone()
            connection.commit()
        if not row:
            raise KeyError(f"Alert {alert.id} not found")
        return self._from_row(row)

    @staticmethod
    def _from_row(row: tuple) -> PriceAlert:
        return PriceAlert(
            id=row[0], hotel_id=row[1], check_in=row[2], check_out=row[3], guests=row[4],
            rooms=row[5], target_price=float(row[6]), currency=row[7], enabled=row[8],
            created_at=row[9], triggered_at=row[10],
        )
