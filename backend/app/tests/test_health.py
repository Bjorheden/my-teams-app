# app/tests/test_health.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – FastAPI TestClient
#
# FastAPI ships with a TestClient that wraps httpx.
# It lets you send real HTTP requests to your app WITHOUT starting
# a server – everything runs in-process, making tests instant.
#
# Pattern:
#   client = TestClient(app)
#   response = client.get("/v1/healthz")
#   assert response.status_code == 200
#
# Why test the health endpoints?
#   1. Proves the app boots without errors (imports work, config loads)
#   2. Proves routing is wired correctly
#   3. Gives us a green CI baseline before adding real features
# ─────────────────────────────────────────────────────────────────

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── /v1/healthz tests ───────────────────────────────────────────

class TestHealthz:
    def test_returns_200(self) -> None:
        response = client.get("/v1/healthz")
        assert response.status_code == 200

    def test_returns_ok_status(self) -> None:
        response = client.get("/v1/healthz")
        data = response.json()
        assert data["status"] == "ok"

    def test_content_type_is_json(self) -> None:
        response = client.get("/v1/healthz")
        assert "application/json" in response.headers["content-type"]


# ── /v1/readyz tests ────────────────────────────────────────────

class TestReadyz:
    def test_returns_200(self) -> None:
        response = client.get("/v1/readyz")
        assert response.status_code == 200

    def test_returns_ready_status(self) -> None:
        response = client.get("/v1/readyz")
        data = response.json()
        assert data["status"] == "ready"

    def test_has_checks_field(self) -> None:
        response = client.get("/v1/readyz")
        data = response.json()
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_mock_data_check_is_ok(self) -> None:
        response = client.get("/v1/readyz")
        data = response.json()
        assert data["checks"].get("mock_data") == "ok"

    def test_has_version_field(self) -> None:
        response = client.get("/v1/readyz")
        data = response.json()
        assert "version" in data

    def test_has_environment_field(self) -> None:
        response = client.get("/v1/readyz")
        data = response.json()
        assert "environment" in data


# ── Root redirect test ───────────────────────────────────────────

def test_root_returns_200() -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
