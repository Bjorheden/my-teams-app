# MyTeams – Personalized Football Hub

> **Learning-first project.** We build a working MVP while learning Docker,
> Docker Compose, GitHub Actions CI/CD and full-stack development step by step.
> Production readiness is *not* the goal. Understanding *why* each piece exists is.

---

## Project Overview

| Layer | Tech |
|-------|------|
| Mobile | React Native + Expo + TypeScript |
| Backend | Python 3.12 + FastAPI |
| Data | Mock data only (no external APIs yet) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## Checkpoint Map

| # | Name | What you learn | Status |
|---|------|----------------|--------|
| 1 | Hello Containers | FastAPI basics, Dockerfile, Compose | ✅ Done |
| 2 | Mock Data API | REST design, in-memory state, schemas | ✅ Done |
| 3 | Mobile Connects | Expo + fetch, basic screens | ✅ Done |
| 4 | Quality Gates | ruff, pytest, GitHub Actions CI | ⬜ |
| 5 | Docker in CI | Build image in Actions, smoke test | ⬜ |
| 6 | State Upgrade | SQLite + SQLAlchemy | ⬜ |
| 7 | Compose Upgrade | Postgres service, env-driven config | ⬜ |
| 8 | Minimal CD | GHCR push / artifact upload | ⬜ |

---

## Checkpoint 1 – Hello Containers

### What we build
- FastAPI app with `GET /v1/healthz` and `GET /v1/readyz`
- A `Dockerfile` for the backend
- A `docker-compose.yml` to run everything with one command
- A `Makefile` with short wrapper commands

### Why this way?
- **FastAPI** gives us automatic OpenAPI docs and is fast to iterate on.
- **Dockerfile** teaches the container build layer model (each `RUN` = one layer).
- **Compose** removes "works on my machine" problems by codifying the runtime env.
- **Makefile** is a simple, portable task runner – no extra tooling needed.

### Commands

```bash
# 1. Copy environment file
cp .env.example .env          # Windows: copy .env.example .env

# 2. Build and start containers (detached mode)
make up

# 3. Verify health endpoints
curl http://localhost:8000/v1/healthz
# Expected: {"status":"ok"}

curl http://localhost:8000/v1/readyz
# Expected: {"status":"ready","checks":{"mock_data":"ok"}}

# 4. View auto-generated API docs in browser
#    http://localhost:8000/docs

# 5. Stop containers
make down
```

### Definition of Done ✅
- [ ] `docker compose up --build` completes without errors
- [ ] `curl http://localhost:8000/v1/healthz` returns `{"status":"ok"}`
- [ ] `curl http://localhost:8000/v1/readyz` returns JSON with `"status":"ready"`
- [ ] `http://localhost:8000/docs` shows Swagger UI with 2 endpoints
- [ ] `make down` stops and removes containers cleanly

---

## Checkpoint 2 – Mock Data API

### What we build (next)
- `GET /v1/teams/search?q=&limit=` – search mock teams
- `GET /v1/me/dashboard` – personalised dashboard with mock fixtures + standings
- `POST /v1/me/follows`, `GET /v1/me/follows`, `DELETE /v1/me/follows/{teamId}`
- In-memory store for follows (single demo user, no auth yet)
- Pydantic response schemas

### Why this way?
- In-memory store is the simplest possible state – no DB setup needed yet.
- Pydantic schemas enforce the API contract and appear in OpenAPI docs for free.
- We skip auth intentionally to stay focused on data modelling.

---

## Checkpoint 3 – Mobile Connects

### What we build (next)
- Expo app with two screens: Team Search and Dashboard
- `fetch` calls to the backend running in Docker
- Basic navigation with Expo Router

---

## Checkpoint 4 – Quality Gates

### What we build (next)
- `ruff` for linting and formatting (replaces flake8 + black + isort)
- `pytest` with a few meaningful tests
- GitHub Actions workflow that runs lint + tests on every push/PR

### Why ruff instead of flake8?
- ruff is 10–100× faster and replaces multiple tools in one binary.

---

## Checkpoint 5 – Docker in CI

### What we build (next)
- CI step that builds the backend Docker image
- CI step that starts the container and hits `/v1/healthz` as a smoke test

### Why?
- Proves the image is buildable and the app actually starts – not just "tests pass locally".

---

## Checkpoint 6 – State Upgrade (SQLite)

### What we build (next)
- SQLAlchemy models for Follows
- SQLite file-based database (zero extra infra)
- Alembic migration (optional learning step)

---

## Checkpoint 7 – Compose Upgrade (Postgres)

### What we build (next)
- Postgres service in `docker-compose.yml`
- Environment-variable-driven `DATABASE_URL`
- Health-check dependency so backend waits for DB

---

## Checkpoint 8 – Minimal CD

### What we build (next)
- Manual-trigger GitHub Actions workflow
- Builds backend Docker image and pushes to GHCR
- Or: saves image as a `.tar` artifact attached to the workflow run

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | `8000` | Host port mapped to the backend container |
| `ENVIRONMENT` | `development` | App environment tag |
| `LOG_LEVEL` | `info` | Uvicorn log level (`debug`/`info`/`warning`) |
| `DATABASE_URL` | *(CP6+)* | SQLAlchemy connection string |

---

## Repository Structure

```
/
├── README.md                  ← you are here
├── docker-compose.yml         ← service definitions
├── .env.example               ← env variable template (safe to commit)
├── Makefile                   ← convenience commands
├── backend/
│   ├── README.md
│   ├── Dockerfile
│   ├── pyproject.toml         ← deps + ruff/mypy config
│   └── app/
│       ├── main.py            ← FastAPI app factory
│       ├── api/               ← route modules
│       │   ├── health.py
│       │   ├── teams.py       ← CP2
│       │   └── me.py          ← CP2
│       ├── core/
│       │   └── config.py      ← settings via pydantic-settings
│       ├── mockdata/
│       │   └── fixtures.py    ← deterministic mock datasets
│       └── tests/
│           └── test_health.py
├── mobile/
│   ├── README.md
│   ├── package.json
│   ├── tsconfig.json
│   └── app/                   ← Expo Router screens (CP3)
└── .github/
    └── workflows/
        ├── ci.yml             ← CI pipeline
        └── cd.yml             ← CD pipeline (CP8)
```

---

## Quick Reference

```bash
make up        # build images and start all services (detached)
make down      # stop and remove containers + networks
make logs      # tail all service logs
make shell     # interactive bash inside backend container
make test      # run pytest inside backend container
make lint      # run ruff check inside backend container
make fmt       # run ruff format inside backend container
```

---

## Assumptions

1. Docker Desktop is installed (Windows with WSL2 backend recommended).
2. Node.js ≥ 18 and `npm` are installed for the mobile app.
3. Python 3.12 is optional locally – Docker is the primary runtime.
4. The mobile app runs **outside** Docker via Expo Go or an emulator/simulator.
5. All data is mock – no external football API keys needed.
6. Single "demo user" assumed throughout – auth is a future concern.
