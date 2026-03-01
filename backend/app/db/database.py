# app/db/database.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – SQLAlchemy session management
#
# Three things live here:
#
# 1. `engine`  – the single connection to the database file.
#    Think of it as the "database handle". Created once at startup.
#
# 2. `SessionLocal` – a factory that creates Session objects.
#    A Session is like a shopping basket: you add/remove objects,
#    then call commit() to write them all to the DB at once.
#    Each HTTP request gets its own Session (→ no shared mutable state).
#
# 3. `get_db()` – a FastAPI dependency (used with Depends()).
#    It opens a session at the start of every request and closes it
#    at the end, even if an exception is raised (the try/finally).
#
# LEARNING NOTE – `check_same_thread=False`
#    SQLite default: only the thread that created the connection can
#    use it. FastAPI runs multiple threads, so we disable this check.
#    SQLAlchemy's connection pool handles thread safety instead.
# ─────────────────────────────────────────────────────────────────

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# ── Engine ───────────────────────────────────────────────────────

engine = create_engine(
    settings.database_url,
    # Required for SQLite – FastAPI uses a thread pool so multiple
    # threads may access the same connection.
    connect_args={"check_same_thread": False},
)

# ── Session factory ───────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,  # we call commit() ourselves
    autoflush=False,  # we control when queries are sent to DB
    bind=engine,
)

# ── Declarative base ──────────────────────────────────────────────
# All ORM model classes inherit from Base.
# SQLAlchemy uses this to discover which tables to create.


class Base(DeclarativeBase):
    pass


# ── FastAPI dependency ────────────────────────────────────────────


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for one HTTP request.

    Usage in a route:
        async def my_route(db: Annotated[Session, Depends(get_db)]):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
