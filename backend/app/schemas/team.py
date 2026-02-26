# app/schemas/team.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Pydantic response schemas
#
# These classes define the SHAPE of what the API returns.
# FastAPI uses them to:
#   1. Validate that your route handler returns the right data
#   2. Serialize the response to JSON automatically
#   3. Generate accurate OpenAPI docs (shown in /docs)
#
# Rule of thumb: one schema per "thing" the API returns.
# Separate input schemas (what the client sends) from output schemas
# (what the server returns) – they often differ.
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel


class TeamOut(BaseModel):
    """A single football team as returned by the API."""

    id: str
    name: str
    short_name: str
    country: str
    league: str
    crest_emoji: str


class TeamSearchResponse(BaseModel):
    """Envelope for the team search results."""

    results: list[TeamOut]
    count: int  # number of results returned (≤ limit)
    query: str  # the search term that was used
