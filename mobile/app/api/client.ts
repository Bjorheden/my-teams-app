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
// This is a minimal client – no caching, no retry, no auth headers yet.
// Those would be added in a production app or when we introduce auth.
// ─────────────────────────────────────────────────────────────────

import { API_V1 } from "../config";
import type {
  DashboardOut,
  FollowOut,
  FollowsResponse,
  TeamSearchResponse,
  UnfollowResponse,
} from "../types";

// ── Core helper ──────────────────────────────────────────────────

const TIMEOUT_MS = 8_000;

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_V1}${path}`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
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
