def test_system_readiness_and_metrics(client) -> None:
    ready_response = client.get("/api/v1/system/ready")
    metrics_response = client.get("/api/v1/system/metrics")

    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"

    assert metrics_response.status_code == 200
    metrics_payload = metrics_response.json()
    assert "requests_total" in metrics_payload
    assert "status_codes" in metrics_payload


def test_create_alert_for_demo_user(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "alerts@cryptopulse.ai", "password": "AlertsPass123!"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "alerts@cryptopulse.ai", "password": "AlertsPass123!"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "symbol": "ETH",
            "alert_type": "price_above",
            "threshold": 3800,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["symbol"] == "ETH"
    assert payload["alert_type"] == "price_above"
