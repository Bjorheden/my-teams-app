# app/api/health.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Health vs Readiness probes
#
# Two separate endpoints are a Kubernetes convention (and just good practice):
#
#   /healthz  – LIVENESS probe
#     "Is the process alive?"
#     Returns 200 as long as the process is running.
#     If this fails → restart the container.
#
#   /readyz   – READINESS probe
#     "Is the app ready to accept traffic?"
#     Checks that dependencies (DB, mock data, etc.) are reachable.
#     If this fails → stop routing traffic to this instance (but don't restart).
#
# For CP1 there's no real DB, so readyz just confirms mock data loaded.
# In CP6+ readyz will check the DB connection.
# ─────────────────────────────────────────────────────────────────

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter(tags=["health"])


# ── Response schemas ────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str  # "ok"


class ReadyzResponse(BaseModel):
    status: str  # "ready" | "degraded"
    checks: dict[str, str]  # name → "ok" | "error"
    version: str
    environment: str


# ── Endpoints ───────────────────────────────────────────────────


@router.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Returns 200 OK if the process is alive.",
)
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/readyz",
    response_model=ReadyzResponse,
    summary="Readiness probe",
    description="Returns 200 if the app is ready to serve traffic. "
    "Checks that all dependencies are reachable.",
)
async def readyz() -> ReadyzResponse:
    # CP1: no real dependencies yet – just confirm mock data module imports.
    checks: dict[str, str] = {}

    try:
        # Import mock data to confirm the module loads cleanly.
        from app.mockdata import fixtures  # noqa: F401

        checks["mock_data"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["mock_data"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    return ReadyzResponse(
        status="ready" if all_ok else "degraded",
        checks=checks,
        version=settings.app_version,
        environment=settings.environment,
    )
