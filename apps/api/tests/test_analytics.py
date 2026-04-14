def test_anomalies_endpoint_returns_ranked_records(client) -> None:
    response = client.get("/api/v1/analytics/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["anomalies"]) >= 1
    assert payload["anomalies"][0]["symbol"] == "SOL"
    assert len(payload["recommendations"]) >= 1


def test_summary_endpoint_supports_market_and_symbol_scope(client) -> None:
    market_response = client.get("/api/v1/analytics/summary")
    btc_response = client.get("/api/v1/analytics/summary", params={"scope": "BTC"})

    assert market_response.status_code == 200
    assert btc_response.status_code == 200
    assert market_response.json()["scope"] == "market"
    assert btc_response.json()["scope"] == "BTC"
