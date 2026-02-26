# app/tests/test_teams.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Testing query parameters
#
# FastAPI's TestClient passes query params as a `params` dict:
#   client.get("/v1/teams/search", params={"q": "arsenal", "limit": 3})
# This is cleaner than manually building query strings.
# ─────────────────────────────────────────────────────────────────

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestTeamSearch:
    def test_empty_query_returns_all_teams(self) -> None:
        response = client.get("/v1/teams/search")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 10          # default limit=10
        assert data["query"] == ""
        assert len(data["results"]) == 10

    def test_search_by_name(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "arsenal"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Arsenal FC"

    def test_search_is_case_insensitive(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "ARSENAL"})
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_search_by_country(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "spain"})
        assert response.status_code == 200
        data = response.json()
        # Barcelona, Real Madrid, Atletico
        assert data["count"] == 3

    def test_search_by_league(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "bundesliga"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2   # Bayern + Dortmund

    def test_limit_is_respected(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "", "limit": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["results"]) == 3

    def test_no_match_returns_empty_list(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "zzznomatch"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_result_has_expected_fields(self) -> None:
        response = client.get("/v1/teams/search", params={"q": "liverpool"})
        assert response.status_code == 200
        team = response.json()["results"][0]
        for field in ("id", "name", "short_name", "country", "league", "crest_emoji"):
            assert field in team

    def test_invalid_limit_returns_422(self) -> None:
        # limit=0 violates ge=1 constraint → FastAPI returns 422
        response = client.get("/v1/teams/search", params={"limit": 0})
        assert response.status_code == 422


class TestGetTeamById:
    def test_valid_team_id(self) -> None:
        response = client.get("/v1/teams/t01")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "t01"
        assert data["name"] == "Manchester United"

    def test_invalid_team_id_returns_404(self) -> None:
        response = client.get("/v1/teams/doesnotexist")
        assert response.status_code == 404
