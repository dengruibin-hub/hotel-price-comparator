from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_compare_endpoint_returns_three_platforms():
    response = client.post(
        "/api/compare",
        json={
            "hotel_name": "上海外滩某酒店",
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "guests": 2,
            "rooms": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["matched_sources"] == ["amap", "qunar", "zhixing"]
    assert body["lowest_source"] == "zhixing"
    assert body["lowest_price"] == 568
    assert body["savings"] == 52
    assert body["match_score"] > 0


def test_price_history_and_trend_endpoints():
    snapshot_payload = {
        "hotel_id": 1,
        "source": "zhixing",
        "room_type": "高级大床房",
        "check_in": "2026-10-10",
        "check_out": "2026-10-12",
        "guests": 2,
        "rooms": 1,
        "room_price": 560,
        "tax": 0,
        "fees": 0,
        "total_price": 560,
        "currency": "CNY",
        "breakfast": True,
        "cancelable": True,
        "checked_at": "2026-09-06T10:00:00Z",
    }
    create_response = client.post("/api/price-snapshots", json=snapshot_payload)
    assert create_response.status_code == 201

    history_response = client.get(
        "/api/price-history",
        params={
            "hotel_id": 1,
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "guests": 2,
            "rooms": 1,
        },
    )
    assert history_response.status_code == 200
    assert len(history_response.json()["snapshots"]) >= 1

    trend_response = client.get(
        "/api/price-trend",
        params={
            "hotel_id": 1,
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "guests": 2,
            "rooms": 1,
            "days": 30,
        },
    )
    assert trend_response.status_code == 200
    trend = trend_response.json()
    assert trend["current_lowest"] == 560
    assert trend["historical_lowest"] == 560


def test_price_alert_create_list_and_check():
    create_response = client.post(
        "/api/price-alerts",
        json={
            "hotel_id": 2,
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "guests": 2,
            "rooms": 1,
            "target_price": 570,
            "currency": "CNY",
            "enabled": True,
        },
    )
    assert create_response.status_code == 201
    alert = create_response.json()
    assert alert["id"] >= 1

    snapshot_response = client.post(
        "/api/price-snapshots",
        json={
            "hotel_id": 2,
            "source": "qunar",
            "room_type": "高级大床房",
            "check_in": "2026-10-10",
            "check_out": "2026-10-12",
            "guests": 2,
            "rooms": 1,
            "room_price": 550,
            "tax": 0,
            "fees": 0,
            "total_price": 550,
            "currency": "CNY",
            "breakfast": False,
            "cancelable": True,
            "checked_at": "2026-09-06T11:00:00Z",
        },
    )
    assert snapshot_response.status_code == 201

    list_response = client.get("/api/price-alerts", params={"hotel_id": 2})
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1

    check_response = client.post("/api/price-alerts/check")
    assert check_response.status_code == 200
    results = [item for item in check_response.json() if item["alert_id"] == alert["id"]]
    assert len(results) == 1
    assert results[0]["triggered"] is True
    assert results[0]["current_lowest"] == 550
