# app/schemas/fixture.py

from pydantic import BaseModel


class FixtureOut(BaseModel):
    """A single match fixture (past or upcoming)."""
    id: str
    home_team_id: str
    home_team_name: str
    away_team_id: str
    away_team_name: str
    home_goals: int | None    # None if match not played yet
    away_goals: int | None
    date: str                 # ISO 8601 date string, e.g. "2026-02-22"
    status: str               # "finished" | "scheduled"
    competition: str


class StandingRow(BaseModel):
    """One row in a league standings table."""
    position: int
    team_id: str
    team_name: str
    played: int
    won: int
    drawn: int
    lost: int
    gf: int       # goals for
    ga: int       # goals against
    gd: int       # goal difference (computed)
    points: int
