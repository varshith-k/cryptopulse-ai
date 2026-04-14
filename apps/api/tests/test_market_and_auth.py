def test_market_overview_uses_seeded_database(client) -> None:
    response = client.get("/api/v1/market/overview")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["assets"]) >= 4
    assert payload["assets"][0]["symbol"] == "SOL"


def test_login_and_fetch_alerts(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@cryptopulse.ai", "password": "SecurePass123!"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@cryptopulse.ai", "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    create_alert_response = client.post(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "symbol": "BTC",
            "alert_type": "price_above",
            "threshold": 70000,
        },
    )
    assert create_alert_response.status_code == 201

    alerts_response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert alerts_response.status_code == 200
    payload = alerts_response.json()
    assert len(payload) >= 1
    assert payload[0]["symbol"] == "BTC"
