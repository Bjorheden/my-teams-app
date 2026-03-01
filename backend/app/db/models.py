# app/db/models.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – SQLAlchemy ORM models
#
# An ORM (Object Relational Mapper) lets you define database tables
# as Python classes. Each class = one table. Each attribute = one column.
#
# SQLAlchemy 2.0 uses `Mapped[type]` annotations to declare columns.
# This gives you full type safety – mypy knows the column types.
#
# The `Follow` table stores which user follows which team.
# Right now we only have one demo user ("demo"), which keeps the code
# simple. CP7+ would add a proper users table.
#
# UniqueConstraint: prevents the same user from following the same
# team twice at the database level – a safety net on top of the 409
# check in the API. Defense in depth.
# ─────────────────────────────────────────────────────────────────

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

# The single demo user ID used throughout this checkpoint.
# CP7 would replace this with real auth.
DEMO_USER_ID = "demo"


class Follow(Base):
    """One row = one user following one team."""

    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    team_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Database-level uniqueness guarantee: same user can't follow same team twice.
    __table_args__ = (UniqueConstraint("user_id", "team_id", name="uq_user_team"),)

    def __repr__(self) -> str:
        return f"<Follow user={self.user_id!r} team={self.team_id!r}>"
