// mobile/app/api/client.ts
// ─────────────────────────────────────────────────────────────────
// LEARNING NOTE – Typed fetch wrapper
//
// React Native has `fetch` built in (same API as browser fetch).
// We wrap it here so that:
//   1. The base URL is in one place (config.ts)
//   2. Every response is typed – callers get autocomplete + type safety
//   3. Errors are handled consistently (throws on non-2xx)
//
// CP9 CHANGE: Added auth token support.
//   `setToken(token)` stores the JWT in module memory.
//   All requests automatically include `Authorization: Bearer <token>`
//   when a token is set.
// ─────────────────────────────────────────────────────────────────

import { API_V1 } from "../config";
import type {
  DashboardOut,
  FollowOut,
  FollowsResponse,
  TeamSearchResponse,
  TokenOut,
  UnfollowResponse,
  UserOut,
} from "../types";

// ── Token management ─────────────────────────────────────────────
// The token lives here in module memory (loaded from SecureStore on app start).
// AuthContext calls setToken() after login/logout/restore.
//
// onUnauthorized: a callback that AuthContext registers so that any 401
// response (e.g. stale token after a DB reset) automatically clears the
// session and redirects to login — without the user having to do anything.

let _token: string | null = null;
let _onUnauthorized: (() => void) | null = null;

export function setToken(token: string | null): void {
  _token = token;
}

export function setOnUnauthorized(cb: (() => void) | null): void {
  _onUnauthorized = cb;
}

// ── Core helper ──────────────────────────────────────────────────

const TIMEOUT_MS = 8_000;

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_V1}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  // Build headers: always JSON, add Bearer token when available.
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(_token ? { Authorization: `Bearer ${_token}` } : {}),
  };

  let response: Response;
  try {
    response = await fetch(url, {
      headers,
      signal: controller.signal,
      ...options,
    });
  } catch (e: unknown) {
    const msg = e instanceof Error && e.name === "AbortError"
      ? `Timed out after ${TIMEOUT_MS / 1000}s – is the backend running at ${url}?`
      : `Network error – is the backend running at ${url}?`;
    throw new Error(msg);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    // A 401 means our stored token is invalid or expired – clear it so the
    // user is automatically redirected to the login screen.
    if (response.status === 401) {
      _onUnauthorized?.();
    }
    // Attempt to extract the FastAPI error detail
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

// ── Auth ─────────────────────────────────────────────────────────

export function registerUser(email: string, password: string): Promise<TokenOut> {
  return request<TokenOut>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function loginUser(email: string, password: string): Promise<TokenOut> {
  return request<TokenOut>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function getCurrentUser(): Promise<UserOut> {
  return request<UserOut>("/auth/me");
}

// ── Teams ────────────────────────────────────────────────────────

export function searchTeams(
  q: string,
  limit = 10,
): Promise<TeamSearchResponse> {
  const params = new URLSearchParams({ q, limit: String(limit) });
  return request<TeamSearchResponse>(`/teams/search?${params}`);
}

// ── Dashboard ────────────────────────────────────────────────────

export function getDashboard(): Promise<DashboardOut> {
  return request<DashboardOut>("/me/dashboard");
}

// ── Follows ──────────────────────────────────────────────────────

export function getFollows(): Promise<FollowsResponse> {
  return request<FollowsResponse>("/me/follows");
}

export function followTeam(team_id: string): Promise<FollowOut> {
  return request<FollowOut>("/me/follows", {
    method: "POST",
    body: JSON.stringify({ team_id }),
  });
}

export function unfollowTeam(team_id: string): Promise<UnfollowResponse> {
  return request<UnfollowResponse>(`/me/follows/${team_id}`, {
    method: "DELETE",
  });
}
