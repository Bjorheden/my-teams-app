# app/main.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – FastAPI app factory
#
# We create the FastAPI instance here and attach all routers.
# This is called the "app factory" pattern.
#
# Why include_router() instead of defining routes in this file?
#   - Keeps each feature in its own module (health.py, teams.py, …)
#   - main.py stays small and is easy to understand at a glance
#   - Routers can be unit-tested independently
#
# The `prefix="/v1"` means every route is under /v1/...
# Versioning the API from day 1 avoids breaking clients when we make
# breaking changes in v2 later.
# ─────────────────────────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, me, teams
from app.core.config import settings

# ── App instance ────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "MyTeams backend API. "
        "Learning project – mock data only. "
        "See README for checkpoint guide."
    ),
    # Docs are always enabled in this learning project.
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS middleware ─────────────────────────────────────────────
# Required so the Expo app (running on a different port / device IP)
# can call this API from a browser or React Native fetch().
#
# In development we allow all origins (*).
# In production you would list specific origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-only: allow everything
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────
# Each router handles one domain area.
# All are mounted under /v1 to version the API from day 1.

app.include_router(health.router, prefix="/v1")
app.include_router(teams.router, prefix="/v1")  # CP2: /v1/teams/...
app.include_router(me.router, prefix="/v1")  # CP2: /v1/me/...

# ── Root redirect (convenience) ─────────────────────────────────


@app.get("/", include_in_schema=False)
async def root() -> dict:
    return {
        "message": "MyTeams API",
        "docs": "/docs",
        "health": "/v1/healthz",
        "ready": "/v1/readyz",
    }
