// mobile/app/types/index.ts
// TypeScript interfaces that mirror the backend Pydantic schemas.
// Keep these in sync with backend/app/schemas/*.py
//
// LEARNING NOTE – Why duplicate types?
// The backend and mobile are separate processes that communicate over HTTP.
// TypeScript can't import Python types directly, so we define them here.
// In a larger project you might auto-generate these from the OpenAPI spec
// using a tool like `openapi-typescript`. For now, manual is fine.

// ── Teams ────────────────────────────────────────────────────────

export interface Team {
  id: string;
  name: string;
  short_name: string;
  country: string;
  league: string;
  crest_emoji: string;
}

export interface TeamSearchResponse {
  results: Team[];
  count: number;
  query: string;
}

// ── Fixtures ─────────────────────────────────────────────────────

export interface Fixture {
  id: string;
  home_team_id: string;
  home_team_name: string;
  away_team_id: string;
  away_team_name: string;
  home_goals: number | null;
  away_goals: number | null;
  date: string;
  status: "finished" | "scheduled";
  competition: string;
}

export interface StandingRow {
  position: number;
  team_id: string;
  team_name: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  gf: number;
  ga: number;
  gd: number;
  points: number;
}

// ── Me / Follows ─────────────────────────────────────────────────

export interface FollowOut {
  team_id: string;
  team: Team;
}

export interface FollowsResponse {
  follows: FollowOut[];
  count: number;
}

export interface DashboardOut {
  followed_teams: Team[];
  recent_fixtures: Fixture[];
  standings: StandingRow[];
  message: string;
}

export interface UnfollowResponse {
  message: string;
  team_id: string;
}

// ── Auth ─────────────────────────────────────────────────────────

export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  email: string;
}

// ── API error shape ──────────────────────────────────────────────

export interface ApiError {
  detail: string;
}
