from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException, Query

from models.alert_schemas import PriceAlertCheckResult, PriceAlertCreate, PriceAlertResponse
from models.history_schemas import (
    PriceHistoryResponse,
    PriceSnapshotCreate,
    PriceSnapshotResponse,
    PriceTrendPoint,
    PriceTrendResponse,
)
from models.schemas import CompareRequest, CompareResponse
from repositories.alert_repository import InMemoryPriceAlertRepository, PriceAlert
from repositories.postgres_alert_repository import PostgresPriceAlertRepository
from repositories.price_repository import InMemoryPriceSnapshotRepository, PriceSnapshot
from repositories.postgres_price_repository import PostgresPriceSnapshotRepository
from services.comparator import compare_prices
from services.price_alert import check_and_update_alerts
from services.price_trend import build_price_trend

app = FastAPI(
    title="Hotel Price Comparator",
    version="0.1.0",
    description="Compare normalized hotel prices across Qunar, Zhixing and Amap.",
)

_history_repository = InMemoryPriceSnapshotRepository()
_alert_repository = InMemoryPriceAlertRepository()


def get_history_repository():
    """Use PostgreSQL when DATABASE_URL is configured, otherwise memory."""
    from database import DATABASE_URL

    return PostgresPriceSnapshotRepository() if DATABASE_URL else _history_repository


def get_alert_repository():
    """Use PostgreSQL when DATABASE_URL is configured, otherwise memory."""
    from database import DATABASE_URL

    return PostgresPriceAlertRepository() if DATABASE_URL else _alert_repository


def alert_response(alert: PriceAlert) -> PriceAlertResponse:
    return PriceAlertResponse(
        id=alert.id,
        hotel_id=alert.hotel_id,
        check_in=alert.check_in,
        check_out=alert.check_out,
        guests=alert.guests,
        rooms=alert.rooms,
        target_price=alert.target_price,
        currency=alert.currency,
        enabled=alert.enabled,
        created_at=alert.created_at,
        triggered_at=alert.triggered_at,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    try:
        return compare_prices(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/price-snapshots", response_model=PriceSnapshotResponse, status_code=201)
def create_price_snapshot(request: PriceSnapshotCreate) -> PriceSnapshotResponse:
    if request.check_out <= request.check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    snapshot = PriceSnapshot(
        hotel_id=request.hotel_id,
        source=request.source,
        room_type=request.room_type,
        check_in=request.check_in,
        check_out=request.check_out,
        guests=request.guests,
        rooms=request.rooms,
        room_price=request.room_price,
        tax=request.tax,
        fees=request.fees,
        total_price=request.total_price,
        currency=request.currency,
        breakfast=request.breakfast,
        cancelable=request.cancelable,
        checked_at=request.checked_at or datetime.now(timezone.utc),
    )

    try:
        get_history_repository().save_snapshot(snapshot)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PriceSnapshotResponse(
        hotel_id=snapshot.hotel_id,
        source=snapshot.source,
        room_type=snapshot.room_type,
        check_in=snapshot.check_in,
        check_out=snapshot.check_out,
        guests=snapshot.guests,
        rooms=snapshot.rooms,
        room_price=snapshot.room_price,
        tax=snapshot.tax,
        fees=snapshot.fees,
        total_price=snapshot.total_price,
        currency=snapshot.currency,
        breakfast=snapshot.breakfast,
        cancelable=snapshot.cancelable,
        checked_at=snapshot.checked_at,
    )


@app.get("/api/price-history", response_model=PriceHistoryResponse)
def price_history(
    hotel_id: int = Query(ge=1),
    check_in: date = Query(),
    check_out: date = Query(),
    guests: int = Query(default=2, ge=1),
    rooms: int = Query(default=1, ge=1),
) -> PriceHistoryResponse:
    if check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    try:
        snapshots = get_history_repository().list_history(
            hotel_id, check_in, check_out, guests, rooms
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PriceHistoryResponse(
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        rooms=rooms,
        snapshots=[
            PriceSnapshotResponse(
                hotel_id=item.hotel_id,
                source=item.source,
                room_type=item.room_type,
                check_in=item.check_in,
                check_out=item.check_out,
                guests=item.guests,
                rooms=item.rooms,
                room_price=item.room_price,
                tax=item.tax,
                fees=item.fees,
                total_price=item.total_price,
                currency=item.currency,
                breakfast=item.breakfast,
                cancelable=item.cancelable,
                checked_at=item.checked_at,
            )
            for item in snapshots
        ],
    )


@app.get("/api/price-trend", response_model=PriceTrendResponse)
def price_trend(
    hotel_id: int = Query(ge=1),
    check_in: date = Query(),
    check_out: date = Query(),
    guests: int = Query(default=2, ge=1),
    rooms: int = Query(default=1, ge=1),
    days: int = Query(default=30, ge=1, le=365),
) -> PriceTrendResponse:
    if check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")

    try:
        snapshots = get_history_repository().list_history(
            hotel_id, check_in, check_out, guests, rooms
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    trend = build_price_trend(snapshots, days=days)
    return PriceTrendResponse(
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out,
        guests=guests,
        rooms=rooms,
        days=days,
        current_lowest=trend["current_lowest"],
        historical_lowest=trend["historical_lowest"],
        historical_average=trend["historical_average"],
        change_from_lowest=trend["change_from_lowest"],
        change_from_average=trend["change_from_average"],
        points=[PriceTrendPoint(**point) for point in trend["points"]],
    )


@app.post("/api/price-alerts", response_model=PriceAlertResponse, status_code=201)
def create_price_alert(request: PriceAlertCreate) -> PriceAlertResponse:
    if request.check_out <= request.check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")
    alert = PriceAlert(
        id=0,
        hotel_id=request.hotel_id,
        check_in=request.check_in,
        check_out=request.check_out,
        guests=request.guests,
        rooms=request.rooms,
        target_price=request.target_price,
        currency=request.currency,
        enabled=request.enabled,
        created_at=datetime.now(timezone.utc),
    )
    try:
        return alert_response(get_alert_repository().create(alert))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/price-alerts", response_model=list[PriceAlertResponse])
def list_price_alerts(
    hotel_id: int | None = Query(default=None, ge=1),
) -> list[PriceAlertResponse]:
    try:
        return [alert_response(item) for item in get_alert_repository().list_alerts(hotel_id)]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.patch("/api/price-alerts/{alert_id}", response_model=PriceAlertResponse)
def update_price_alert(alert_id: int, enabled: bool = Query()) -> PriceAlertResponse:
    if alert_id < 1:
        raise HTTPException(status_code=422, detail="alert_id must be positive")
    try:
        repository = get_alert_repository()
        alert = repository.get(alert_id)
        if alert is None:
            raise HTTPException(status_code=404, detail="price alert not found")
        updated = PriceAlert(
            id=alert.id,
            hotel_id=alert.hotel_id,
            check_in=alert.check_in,
            check_out=alert.check_out,
            guests=alert.guests,
            rooms=alert.rooms,
            target_price=alert.target_price,
            currency=alert.currency,
            enabled=enabled,
            created_at=alert.created_at,
            triggered_at=alert.triggered_at,
        )
        return alert_response(repository.update(updated))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/price-alerts/check", response_model=list[PriceAlertCheckResult])
def check_price_alerts() -> list[PriceAlertCheckResult]:
    try:
        results = check_and_update_alerts(get_alert_repository(), get_history_repository())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return [PriceAlertCheckResult(**result) for result in results]
