# app/db/models.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – SQLAlchemy ORM models
#
# An ORM (Object Relational Mapper) lets you define database tables
# as Python classes. Each class = one table. Each attribute = one column.
#
# CP9 CHANGE: Added `User` model and removed the hardcoded DEMO_USER_ID.
# The `Follow` table now links to `User` via a foreign key.
# ─────────────────────────────────────────────────────────────────

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """One row = one registered user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    # LEARNING NOTE – never store plain-text passwords.
    # We store a bcrypt hash here. The original password is never recoverable.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # LEARNING NOTE – relationship()
    # This tells SQLAlchemy that a User has many Follow rows.
    # `back_populates` creates a matching `.user` attribute on Follow.
    # `cascade="all, delete-orphan"` means deleting a user also deletes
    # all their follows automatically.
    follows: Mapped[list["Follow"]] = relationship(
        "Follow", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r}>"


class Follow(Base):
    """One row = one user following one team."""

    __tablename__ = "follows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # LEARNING NOTE – ForeignKey links this column to users.id.
    # The DB enforces referential integrity: you can't have a follow
    # pointing to a user that doesn't exist.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="follows")

    # Database-level uniqueness guarantee: same user can't follow same team twice.
    __table_args__ = (UniqueConstraint("user_id", "team_id", name="uq_user_team"),)

    def __repr__(self) -> str:
        return f"<Follow user_id={self.user_id!r} team={self.team_id!r}>"
