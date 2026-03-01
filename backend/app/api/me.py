# app/api/me.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – REST conventions for sub-resources
#
# The /me prefix represents "the current user" (demo user for now).
# Sub-resources follow the pattern: /me/<resource>
#
# Follow/unfollow uses these HTTP verbs intentionally:
#   POST   /me/follows          → create a follow (add to the set)
#   GET    /me/follows          → read follows
#   DELETE /me/follows/{teamId} → remove a follow
#
# CP6 CHANGE: replaced in-memory `state.followed_team_ids` set with
# real SQLAlchemy DB queries. The HTTP contract (status codes, response
# shapes) is identical – the mobile app requires no changes.
#
# LEARNING NOTE – Depends(get_db)
#   FastAPI injects a fresh database Session into each route function.
#   The session is automatically closed after the request completes
#   (handled by the try/finally in get_db()).
#   `Annotated[Session, Depends(get_db)]` is the idiomatic typed form.
# ─────────────────────────────────────────────────────────────────

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import DEMO_USER_ID, Follow
from app.mockdata.fixtures import (
    FIXTURES,
    STANDINGS_PREMIER_LEAGUE,
    TEAMS_BY_ID,
    get_fixtures_for_team,
)
from app.schemas.fixture import FixtureOut, StandingRow
from app.schemas.me import (
    DashboardOut,
    FollowIn,
    FollowOut,
    FollowsResponse,
    UnfollowResponse,
)
from app.schemas.team import TeamOut

router = APIRouter(prefix="/me", tags=["me"])

# Type alias so route signatures stay short and readable.
DbSession = Annotated[Session, Depends(get_db)]


# ── Helpers ───────────────────────────────────────────────


def _enrich_fixture(f: dict[str, Any]) -> FixtureOut:
    """Add team name strings to a raw fixture dict."""
    home = TEAMS_BY_ID.get(f["home_team_id"], {})
    away = TEAMS_BY_ID.get(f["away_team_id"], {})
    return FixtureOut(
        id=f["id"],
        home_team_id=f["home_team_id"],
        home_team_name=home.get("name", "Unknown"),
        away_team_id=f["away_team_id"],
        away_team_name=away.get("name", "Unknown"),
        home_goals=f["home_goals"],
        away_goals=f["away_goals"],
        date=f["date"],
        status=f["status"],
        competition=f["competition"],
    )


def _enrich_standing(row: dict[str, Any]) -> StandingRow:
    """Add team name to a raw standings row."""
    team = TEAMS_BY_ID.get(row["team_id"], {})
    return StandingRow(
        position=row["position"],
        team_id=row["team_id"],
        team_name=team.get("name", "Unknown"),
        played=row["played"],
        won=row["won"],
        drawn=row["drawn"],
        lost=row["lost"],
        gf=row["gf"],
        ga=row["ga"],
        gd=row["gf"] - row["ga"],
        points=row["points"],
    )


# ── POST /me/follows ─────────────────────────────────────────


@router.post(
    "/follows",
    response_model=FollowOut,
    status_code=201,
    summary="Follow a team",
    description="Add a team to the demo user's followed list. Returns 409 if already following.",  # noqa: E501
)
async def follow_team(body: FollowIn, db: DbSession) -> FollowOut:
    team = TEAMS_BY_ID.get(body.team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team '{body.team_id}' not found.")

    follow = Follow(user_id=DEMO_USER_ID, team_id=body.team_id)
    db.add(follow)
    try:
        db.commit()
    except IntegrityError:
        # UniqueConstraint violation – already following this team
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Already following team '{body.team_id}'.",
        )

    return FollowOut(team_id=body.team_id, team=TeamOut(**team))


# ── GET /me/follows ──────────────────────────────────────────


@router.get(
    "/follows",
    response_model=FollowsResponse,
    summary="List followed teams",
    description="Returns all teams the demo user currently follows.",
)
async def list_follows(db: DbSession) -> FollowsResponse:
    rows = (
        db.query(Follow)
        .filter(Follow.user_id == DEMO_USER_ID)
        .order_by(Follow.team_id)
        .all()
    )
    follows = []
    for row in rows:
        team = TEAMS_BY_ID.get(row.team_id)
        if team:
            follows.append(FollowOut(team_id=row.team_id, team=TeamOut(**team)))

    return FollowsResponse(follows=follows, count=len(follows))


# ── DELETE /me/follows/{teamId} ────────────────────────────────


@router.delete(
    "/follows/{team_id}",
    response_model=UnfollowResponse,
    summary="Unfollow a team",
    description="Remove a team from the demo user's followed list. Returns 404 if not following.",  # noqa: E501
)
async def unfollow_team(team_id: str, db: DbSession) -> UnfollowResponse:
    follow = (
        db.query(Follow)
        .filter(Follow.user_id == DEMO_USER_ID, Follow.team_id == team_id)
        .first()
    )
    if follow is None:
        raise HTTPException(
            status_code=404,
            detail=f"Not following team '{team_id}'.",
        )

    db.delete(follow)
    db.commit()
    return UnfollowResponse(message="Unfollowed successfully.", team_id=team_id)


# ── GET /me/dashboard ──────────────────────────────────────────


@router.get(
    "/dashboard",
    response_model=DashboardOut,
    summary="Get personalised dashboard",
    description=(
        "Returns followed teams, their recent/upcoming fixtures, "
        "and the Premier League standings. "
        "If no teams are followed, returns a welcome message with empty data."
    ),
)
async def get_dashboard(db: DbSession) -> DashboardOut:
    rows = db.query(Follow).filter(Follow.user_id == DEMO_USER_ID).all()
    followed_team_ids = {row.team_id for row in rows}

    followed_teams = [
        TeamOut(**TEAMS_BY_ID[tid])
        for tid in sorted(followed_team_ids)
        if tid in TEAMS_BY_ID
    ]

    # Collect all fixtures for followed teams (deduplicated by fixture id)
    seen_fixture_ids: set[str] = set()
    relevant_fixtures: list[FixtureOut] = []

    for tid in followed_team_ids:
        for f in get_fixtures_for_team(tid):
            if f["id"] not in seen_fixture_ids:
                seen_fixture_ids.add(f["id"])
                relevant_fixtures.append(_enrich_fixture(f))

    # If no teams followed yet, show all fixtures as a preview
    if not followed_teams:
        relevant_fixtures = [_enrich_fixture(f) for f in FIXTURES]

    # Sort: finished matches (most recent first), then scheduled (soonest first)
    finished = sorted(
        [f for f in relevant_fixtures if f.status == "finished"],
        key=lambda f: f.date,
        reverse=True,
    )
    scheduled = sorted(
        [f for f in relevant_fixtures if f.status == "scheduled"],
        key=lambda f: f.date,
    )
    ordered_fixtures = finished + scheduled

    standings = [_enrich_standing(row) for row in STANDINGS_PREMIER_LEAGUE]

    message = (
        "Welcome to MyTeams! Follow some teams to personalise your dashboard."
        if not followed_teams
        else f"Dashboard for {len(followed_teams)} followed team(s)."
    )

    return DashboardOut(
        followed_teams=followed_teams,
        recent_fixtures=ordered_fixtures,
        standings=standings,
        message=message,
    )
