# app/schemas/me.py
# Schemas for the /me routes (follows + dashboard).

from pydantic import BaseModel

from app.schemas.fixture import FixtureOut, StandingRow
from app.schemas.team import TeamOut


# ── Follows ─────────────────────────────────────────────────────

class FollowIn(BaseModel):
    """Request body for POST /v1/me/follows."""
    team_id: str


class FollowOut(BaseModel):
    """A single follow entry returned by the API."""
    team_id: str
    team: TeamOut    # full team details embedded – no second request needed


class FollowsResponse(BaseModel):
    """Envelope for the list of followed teams."""
    follows: list[FollowOut]
    count: int


class UnfollowResponse(BaseModel):
    """Response for DELETE /v1/me/follows/{teamId}."""
    message: str
    team_id: str


# ── Dashboard ────────────────────────────────────────────────────

class DashboardOut(BaseModel):
    """
    Personalised dashboard for the demo user.

    Shows:
    - Teams they follow
    - Recent fixtures involving any followed team
    - Premier League standings (mock, regardless of which teams are followed)
    """
    followed_teams: list[TeamOut]
    recent_fixtures: list[FixtureOut]
    standings: list[StandingRow]
    message: str   # friendly context message
