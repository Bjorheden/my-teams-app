# app/state.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – In-memory state
#
# This module holds application state that lives only in RAM.
#
# Pros:
#   - Zero setup – no DB, no migrations, works immediately
#   - Great for prototyping and learning the API shape
#
# Cons (why we replace it in Checkpoint 6):
#   - Resets to empty every time the container restarts
#   - Can't share state across multiple container replicas
#   - No query capabilities (filtering, sorting at the DB level)
#
# Pattern: we use a plain Python set for followed team IDs.
# A set prevents duplicates automatically (following the same team
# twice is a no-op), and membership check is O(1).
#
# Single "demo user" assumption:
#   There is no auth yet so we store one global set of follows.
#   In a real app this would be a dict keyed by user_id.
#   We'll introduce per-user storage when we add auth (post-CP8).
# ─────────────────────────────────────────────────────────────────

# The set of team IDs the demo user currently follows.
# Type annotation makes it clear what's stored.
followed_team_ids: set[str] = set()
