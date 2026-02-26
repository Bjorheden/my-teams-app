# app/api/teams.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Query parameters
#
# FastAPI automatically reads function parameters that aren't path
# parameters as QUERY parameters. So:
#
#   async def search(q: str = "", limit: int = 10)
#
# …maps to: GET /v1/teams/search?q=arsenal&limit=5
#
# FastAPI also validates types – if the client sends ?limit=abc it
# returns a 422 Unprocessable Entity automatically. You get that
# validation for free just from the type annotation `limit: int`.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter, HTTPException, Query

from app.mockdata.fixtures import TEAMS
from app.schemas.team import TeamOut, TeamSearchResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get(
    "/search",
    response_model=TeamSearchResponse,
    summary="Search teams",
    description=(
        "Search for teams by name, short name, country, or league. "
        "Case-insensitive substring match. Returns up to `limit` results."
    ),
)
async def search_teams(
    q: str = Query(default="", description="Search query (name, country, league)"),
    limit: int = Query(default=10, ge=1, le=50, description="Max results to return"),
) -> TeamSearchResponse:
    # ── Filter ───────────────────────────────────────────────────
    # Lowercase everything for case-insensitive matching.
    # We search across name, short_name, country, and league.
    query = q.strip().lower()

    if query == "":
        # Empty query returns all teams (up to limit)
        matched = TEAMS[:limit]
    else:
        matched = [
            t for t in TEAMS
            if query in t["name"].lower()
            or query in t["short_name"].lower()
            or query in t["country"].lower()
            or query in t["league"].lower()
        ][:limit]

    return TeamSearchResponse(
        results=[TeamOut(**t) for t in matched],
        count=len(matched),
        query=q,
    )


@router.get(
    "/{team_id}",
    response_model=TeamOut,
    summary="Get a team by ID",
    description="Returns a single team by its stable ID (e.g. `t01`).",
)
async def get_team(team_id: str) -> TeamOut:
    from app.mockdata.fixtures import TEAMS_BY_ID

    team = TEAMS_BY_ID.get(team_id)
    if team is None:
        # FastAPI catches this and returns a 404 JSON response
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found.")
    return TeamOut(**team)
