def test_register_then_fetch_profile(client) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@cryptopulse.ai", "password": "StrongerPass123!"},
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "newuser@cryptopulse.ai", "password": "StrongerPass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    profile_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "newuser@cryptopulse.ai"
