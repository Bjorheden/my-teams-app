# app/mockdata/fixtures.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Why hardcoded mock data?
#
# External football APIs require API keys, have rate limits, and add
# network variability to development. Mock data lets us:
#   1. Build and test the full API shape offline
#   2. Keep tests fast, deterministic, and free
#   3. Parallelize frontend and backend development
#
# Convention: all mock data is defined as Python dicts/lists so it
# can be imported directly without any DB or file I/O.
# In CP2 we'll expose this data through endpoints with Pydantic schemas.
# ─────────────────────────────────────────────────────────────────

from typing import Any

# ── Teams ───────────────────────────────────────────────────────
# Each team has a stable `id` – used in follow/unfollow operations.

TEAMS: list[dict[str, Any]] = [
    {"id": "t01", "name": "Manchester United", "short_name": "MAN UTD",  "country": "England", "league": "Premier League", "crest_emoji": "🔴"},
    {"id": "t02", "name": "Liverpool FC",       "short_name": "LIV",      "country": "England", "league": "Premier League", "crest_emoji": "🔴"},
    {"id": "t03", "name": "Arsenal FC",         "short_name": "ARS",      "country": "England", "league": "Premier League", "crest_emoji": "🔴"},
    {"id": "t04", "name": "Chelsea FC",         "short_name": "CHE",      "country": "England", "league": "Premier League", "crest_emoji": "🔵"},
    {"id": "t05", "name": "Manchester City",    "short_name": "MAN CITY", "country": "England", "league": "Premier League", "crest_emoji": "🔵"},
    {"id": "t06", "name": "Tottenham Hotspur",  "short_name": "TOT",      "country": "England", "league": "Premier League", "crest_emoji": "⚪"},
    {"id": "t07", "name": "FC Barcelona",       "short_name": "BAR",      "country": "Spain",   "league": "La Liga",        "crest_emoji": "🔵🔴"},
    {"id": "t08", "name": "Real Madrid CF",     "short_name": "RMA",      "country": "Spain",   "league": "La Liga",        "crest_emoji": "⚪"},
    {"id": "t09", "name": "Atlético de Madrid", "short_name": "ATM",      "country": "Spain",   "league": "La Liga",        "crest_emoji": "🔴⚪"},
    {"id": "t10", "name": "FC Bayern München",  "short_name": "BAY",      "country": "Germany", "league": "Bundesliga",     "crest_emoji": "🔴"},
    {"id": "t11", "name": "Borussia Dortmund",  "short_name": "BVB",      "country": "Germany", "league": "Bundesliga",     "crest_emoji": "🟡"},
    {"id": "t12", "name": "Juventus FC",        "short_name": "JUV",      "country": "Italy",   "league": "Serie A",        "crest_emoji": "⚫⚪"},
    {"id": "t13", "name": "AC Milan",           "short_name": "MIL",      "country": "Italy",   "league": "Serie A",        "crest_emoji": "🔴⚫"},
    {"id": "t14", "name": "Inter Milan",        "short_name": "INT",      "country": "Italy",   "league": "Serie A",        "crest_emoji": "🔵⚫"},
    {"id": "t15", "name": "Paris Saint-Germain","short_name": "PSG",      "country": "France",  "league": "Ligue 1",        "crest_emoji": "🔵🔴"},
]

# Index by id for O(1) lookup
TEAMS_BY_ID: dict[str, dict[str, Any]] = {t["id"]: t for t in TEAMS}

# ── Recent Fixtures ─────────────────────────────────────────────
# A small set of mock recent matches.
# status: "finished" | "scheduled"

FIXTURES: list[dict[str, Any]] = [
    {
        "id": "f001",
        "home_team_id": "t01", "away_team_id": "t02",
        "home_goals": 2, "away_goals": 1,
        "date": "2026-02-22", "status": "finished",
        "competition": "Premier League",
    },
    {
        "id": "f002",
        "home_team_id": "t07", "away_team_id": "t08",
        "home_goals": 1, "away_goals": 3,
        "date": "2026-02-23", "status": "finished",
        "competition": "La Liga",
    },
    {
        "id": "f003",
        "home_team_id": "t10", "away_team_id": "t11",
        "home_goals": 4, "away_goals": 0,
        "date": "2026-02-23", "status": "finished",
        "competition": "Bundesliga",
    },
    {
        "id": "f004",
        "home_team_id": "t03", "away_team_id": "t05",
        "home_goals": None, "away_goals": None,
        "date": "2026-03-01", "status": "scheduled",
        "competition": "Premier League",
    },
    {
        "id": "f005",
        "home_team_id": "t08", "away_team_id": "t09",
        "home_goals": None, "away_goals": None,
        "date": "2026-03-02", "status": "scheduled",
        "competition": "La Liga",
    },
]

# ── Standings (mini table) ───────────────────────────────────────
# Simplified standings for the Premier League.

STANDINGS_PREMIER_LEAGUE: list[dict[str, Any]] = [
    {"position": 1, "team_id": "t05", "played": 26, "won": 18, "drawn": 5, "lost": 3, "gf": 62, "ga": 28, "points": 59},
    {"position": 2, "team_id": "t03", "played": 26, "won": 17, "drawn": 4, "lost": 5, "gf": 55, "ga": 24, "points": 55},
    {"position": 3, "team_id": "t02", "played": 26, "won": 16, "drawn": 5, "lost": 5, "gf": 58, "ga": 33, "points": 53},
    {"position": 4, "team_id": "t06", "played": 26, "won": 14, "drawn": 6, "lost": 6, "gf": 47, "ga": 38, "points": 48},
    {"position": 5, "team_id": "t04", "played": 26, "won": 13, "drawn": 5, "lost": 8, "gf": 44, "ga": 37, "points": 44},
    {"position": 6, "team_id": "t01", "played": 26, "won": 11, "drawn": 7, "lost": 8, "gf": 40, "ga": 42, "points": 40},
]


def get_fixtures_for_team(team_id: str) -> list[dict[str, Any]]:
    """Return all fixtures (finished or scheduled) that involve `team_id`."""
    return [
        f for f in FIXTURES
        if f["home_team_id"] == team_id or f["away_team_id"] == team_id
    ]
