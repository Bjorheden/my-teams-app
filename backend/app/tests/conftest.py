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
# Why monkeypatch instead of dependency_overrides?
#   FastAPI's `dependency_overrides` requires the overriding callable
#   to match how FastAPI resolves the dependency at request time.
#   In some async-route configurations the override may silently be
#   skipped.  Monkeypatching the module-level `SessionLocal` variable
#   is simpler and more reliable: Python functions always look up
#   globals through the module's `__dict__`, so swapping the variable
#   there is guaranteed to be picked up by `get_db()`.
#
# Why StaticPool?
#   Without it, sqlite:///:memory: gives each new connection its OWN
#   empty database.  Base.metadata.create_all() would create tables
#   in connection-A, but SessionLocal() might open connection-B with
#   no tables.  StaticPool forces all connections to reuse the same
#   underlying SQLite database object.
# ─────────────────────────────────────────────────────────────────

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base


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
    # Import models so Base.metadata knows about the Follow table.
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
