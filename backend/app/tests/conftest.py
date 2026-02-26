# app/tests/conftest.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – pytest fixtures and test isolation
#
# The in-memory `state.followed_team_ids` set persists for the
# entire Python process. If test A follows a team, test B would
# see that team as followed – making tests ORDER-DEPENDENT (bad!).
#
# The fix: a pytest fixture with `autouse=True` that runs before
# every test and resets the state to empty.
#
# `autouse=True` means the fixture is applied automatically to
# every test in any file that imports from this conftest.py
# (i.e., every test in the same directory or below).
# ─────────────────────────────────────────────────────────────────

import pytest

from app import state


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Clear in-memory follows before every test for full isolation."""
    state.followed_team_ids.clear()
    yield
    # (teardown code would go here after `yield` if needed)
