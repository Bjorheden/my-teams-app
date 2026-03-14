# app/tests/conftest.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – test isolation with SQLAlchemy
#
# CP6 uses a real database, so we need a different isolation strategy
# from CP2's simple `state.followed_team_ids.clear()`.
#
# The pattern used here:
#   1. A fresh in-memory SQLite engine is created for each test.
#      (StaticPool = all connections within one engine share the same
#       in-memory SQLite database object.)
#   2. `monkeypatch` swaps out `SessionLocal` in the `database` module
#      so that the production `get_db()` function automatically uses
#      the test engine – no FastAPI `dependency_overrides` needed.
#   3. `monkeypatch` automatically restores the original `SessionLocal`
#      after each test, guaranteeing a clean state.
#
# CP9 addition: `auth_headers` fixture registers a test user and returns
# the Authorization header dict so tests can call protected endpoints.
# ─────────────────────────────────────────────────────────────────

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.main import app


@pytest.fixture(autouse=True)
def reset_db(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """
    Per-test fixture:
    - Creates a fresh in-memory SQLite engine (StaticPool).
    - Builds all ORM tables on it.
    - Monkeypatches `SessionLocal` in app.db.database so that the
      production `get_db()` function uses the test engine transparently.
    - Disposes the engine after the test.
    """
    # Import models so Base.metadata knows about the User + Follow tables.
    import app.db.database as db_module
    from app.db import models  # noqa: F401

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    TestLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Swap SessionLocal so get_db() opens sessions from the test engine.
    monkeypatch.setattr(db_module, "SessionLocal", TestLocal)

    yield

    # monkeypatch restores SessionLocal automatically; we just dispose.
    test_engine.dispose()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """
    Register a test user and return the Authorization header dict.
    Use this fixture in any test that calls a protected endpoint.

    Example:
        def test_something(auth_headers):
            response = client.get("/v1/me/follows", headers=auth_headers)
    """
    client = TestClient(app)
    response = client.post(
        "/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 201, f"Auth fixture failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
