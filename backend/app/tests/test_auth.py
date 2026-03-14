# app/tests/test_auth.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── POST /v1/auth/register ────────────────────────────────────


class TestRegister:
    def test_register_returns_201(self) -> None:
        response = client.post(
            "/v1/auth/register",
            json={"email": "user@example.com", "password": "password123"},
        )
        assert response.status_code == 201

    def test_register_returns_token(self) -> None:
        response = client.post(
            "/v1/auth/register",
            json={"email": "user@example.com", "password": "password123"},
        )
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20

    def test_register_duplicate_email_returns_409(self) -> None:
        client.post(
            "/v1/auth/register",
            json={"email": "dupe@example.com", "password": "password123"},
        )
        response = client.post(
            "/v1/auth/register",
            json={"email": "dupe@example.com", "password": "password123"},
        )
        assert response.status_code == 409

    def test_register_short_password_returns_422(self) -> None:
        response = client.post(
            "/v1/auth/register",
            json={"email": "user@example.com", "password": "short"},
        )
        assert response.status_code == 422

    def test_register_invalid_email_returns_422(self) -> None:
        response = client.post(
            "/v1/auth/register",
            json={"email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 422


# ── POST /v1/auth/login ───────────────────────────────────────


class TestLogin:
    def test_login_valid_credentials_returns_token(self) -> None:
        client.post(
            "/v1/auth/register",
            json={"email": "user@example.com", "password": "password123"},
        )
        response = client.post(
            "/v1/auth/login",
            json={"email": "user@example.com", "password": "password123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password_returns_401(self) -> None:
        client.post(
            "/v1/auth/register",
            json={"email": "user@example.com", "password": "password123"},
        )
        response = client.post(
            "/v1/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_unknown_email_returns_401(self) -> None:
        response = client.post(
            "/v1/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )
        assert response.status_code == 401


# ── GET /v1/auth/me ───────────────────────────────────────────


class TestGetMe:
    def test_returns_user_info(self, auth_headers: dict[str, str]) -> None:
        response = client.get("/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_no_token_returns_401(self) -> None:
        response = client.get("/v1/auth/me")
        assert response.status_code == 401
