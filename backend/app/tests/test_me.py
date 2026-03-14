# app/tests/test_me.py

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── POST /v1/me/follows ────────────────────────────────────────


class TestFollowTeam:
    def test_follow_valid_team_returns_201(self, auth_headers: dict[str, str]) -> None:
        response = client.post(
            "/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers
        )
        assert response.status_code == 201

    def test_follow_returns_team_details(self, auth_headers: dict[str, str]) -> None:
        response = client.post(
            "/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers
        )
        data = response.json()
        assert data["team_id"] == "t01"
        assert data["team"]["name"] == "Manchester United"

    def test_follow_invalid_team_returns_404(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/v1/me/follows", json={"team_id": "zzz"}, headers=auth_headers
        )
        assert response.status_code == 404

    def test_follow_duplicate_returns_409(self, auth_headers: dict[str, str]) -> None:
        client.post("/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers)
        response = client.post(
            "/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers
        )
        assert response.status_code == 409

    def test_can_follow_multiple_teams(self, auth_headers: dict[str, str]) -> None:
        client.post("/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers)
        response = client.post(
            "/v1/me/follows", json={"team_id": "t02"}, headers=auth_headers
        )
        assert response.status_code == 201

    def test_unauthenticated_returns_401(self) -> None:
        response = client.post("/v1/me/follows", json={"team_id": "t01"})
        assert response.status_code == 401


# ── GET /v1/me/follows ─────────────────────────────────────────


class TestListFollows:
    def test_empty_by_default(self, auth_headers: dict[str, str]) -> None:
        response = client.get("/v1/me/follows", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["follows"] == []

    def test_returns_followed_team_after_follow(
        self, auth_headers: dict[str, str]
    ) -> None:
        client.post("/v1/me/follows", json={"team_id": "t07"}, headers=auth_headers)
        response = client.get("/v1/me/follows", headers=auth_headers)
        data = response.json()
        assert data["count"] == 1
        assert data["follows"][0]["team"]["name"] == "FC Barcelona"

    def test_count_matches_list_length(self, auth_headers: dict[str, str]) -> None:
        client.post("/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers)
        client.post("/v1/me/follows", json={"team_id": "t02"}, headers=auth_headers)
        client.post("/v1/me/follows", json={"team_id": "t03"}, headers=auth_headers)
        response = client.get("/v1/me/follows", headers=auth_headers)
        data = response.json()
        assert data["count"] == 3
        assert len(data["follows"]) == 3


# ── DELETE /v1/me/follows/{teamId} ────────────────────────────


class TestUnfollowTeam:
    def test_unfollow_followed_team_returns_200(
        self, auth_headers: dict[str, str]
    ) -> None:
        client.post("/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers)
        response = client.delete("/v1/me/follows/t01", headers=auth_headers)
        assert response.status_code == 200

    def test_unfollow_removes_team_from_list(
        self, auth_headers: dict[str, str]
    ) -> None:
        client.post("/v1/me/follows", json={"team_id": "t01"}, headers=auth_headers)
        client.delete("/v1/me/follows/t01", headers=auth_headers)
        response = client.get("/v1/me/follows", headers=auth_headers)
        assert response.json()["count"] == 0

    def test_unfollow_not_following_returns_404(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.delete("/v1/me/follows/t01", headers=auth_headers)
        assert response.status_code == 404

    def test_unfollow_response_contains_team_id(
        self, auth_headers: dict[str, str]
    ) -> None:
        client.post("/v1/me/follows", json={"team_id": "t05"}, headers=auth_headers)
        response = client.delete("/v1/me/follows/t05", headers=auth_headers)
        assert response.json()["team_id"] == "t05"


# ── GET /v1/me/dashboard ─────────────────────────────────────


class TestDashboard:
    def test_returns_200(self, auth_headers: dict[str, str]) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        assert response.status_code == 200

    def test_has_required_fields(self, auth_headers: dict[str, str]) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        data = response.json()
        for field in ("followed_teams", "recent_fixtures", "standings", "message"):
            assert field in data

    def test_empty_followed_teams_by_default(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        data = response.json()
        assert data["followed_teams"] == []

    def test_welcome_message_when_no_follows(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        assert "Welcome" in response.json()["message"]

    def test_shows_all_fixtures_when_no_follows(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        # Should show preview fixtures even with no follows
        assert len(response.json()["recent_fixtures"]) > 0

    def test_followed_team_appears_in_dashboard(
        self, auth_headers: dict[str, str]
    ) -> None:
        client.post("/v1/me/follows", json={"team_id": "t07"}, headers=auth_headers)
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        data = response.json()
        assert len(data["followed_teams"]) == 1
        assert data["followed_teams"][0]["name"] == "FC Barcelona"

    def test_fixtures_for_followed_team_included(
        self, auth_headers: dict[str, str]
    ) -> None:
        # t07 = FC Barcelona, has fixture f002
        client.post("/v1/me/follows", json={"team_id": "t07"}, headers=auth_headers)
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        fixture_ids = [f["id"] for f in response.json()["recent_fixtures"]]
        assert "f002" in fixture_ids

    def test_standings_always_present(self, auth_headers: dict[str, str]) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        standings = response.json()["standings"]
        assert len(standings) > 0
        # First row is league leader
        assert standings[0]["position"] == 1

    def test_standings_rows_have_goal_difference(
        self, auth_headers: dict[str, str]
    ) -> None:
        response = client.get("/v1/me/dashboard", headers=auth_headers)
        row = response.json()["standings"][0]
        assert "gd" in row
        # gd = gf - ga
        assert row["gd"] == row["gf"] - row["ga"]
