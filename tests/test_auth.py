from fastapi.testclient import TestClient


REGISTER_PAYLOAD = {
    "email": "alice@example.com",
    "full_name": "Alice Example",
    "password": "supersecret123",
}


def test_register_creates_user_and_returns_public_profile(http_client: TestClient) -> None:
    response = http_client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert body["full_name"] == REGISTER_PAYLOAD["full_name"]
    assert "id" in body
    assert "created_at" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_conflict(http_client: TestClient) -> None:
    http_client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = http_client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409


def test_login_returns_jwt_access_token(http_client: TestClient) -> None:
    http_client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = http_client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"].split(".")) == 3


def test_login_with_wrong_password_returns_unauthorized(http_client: TestClient) -> None:
    http_client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = http_client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "definitely-wrong"},
    )

    assert response.status_code == 401


def test_get_current_user_returns_authenticated_profile(http_client: TestClient) -> None:
    http_client.post("/auth/register", json=REGISTER_PAYLOAD)
    login_response = http_client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = http_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


def test_get_current_user_without_token_returns_unauthorized(http_client: TestClient) -> None:
    response = http_client.get("/users/me")

    assert response.status_code == 401


def test_get_current_user_with_invalid_token_returns_unauthorized(http_client: TestClient) -> None:
    response = http_client.get(
        "/users/me", headers={"Authorization": "Bearer not-a-real-jwt"}
    )

    assert response.status_code == 401
