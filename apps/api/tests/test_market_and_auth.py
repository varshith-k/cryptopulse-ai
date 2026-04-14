def test_market_overview_uses_seeded_database(client) -> None:
    response = client.get("/api/v1/market/overview")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["assets"]) >= 4
    assert payload["assets"][0]["symbol"] == "SOL"


def test_login_and_fetch_alerts(client) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "demo@cryptopulse.ai", "password": "DemoPass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    alerts_response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert alerts_response.status_code == 200
    payload = alerts_response.json()
    assert len(payload) >= 1
    assert payload[0]["symbol"] == "BTC"
