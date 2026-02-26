# backend/Dockerfile
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Docker layer caching
#
# Docker builds images in layers. Each instruction (FROM, RUN, COPY…)
# creates a new layer. Layers are CACHED: if the files for that layer
# have not changed, Docker reuses the cached layer.
#
# KEY TRICK: Copy requirements BEFORE copying source code.
#   COPY pyproject.toml .          ← only changes when deps change
#   RUN pip install …              ← cached if pyproject.toml unchanged
#   COPY app/ ./app/               ← changes every time you edit code
#
# Without this ordering, every code change would re-run pip install.
# With it, pip install only re-runs when you add/remove a dependency.
# ─────────────────────────────────────────────────────────────────

# Stage: single-stage build (we'll add multi-stage in a later checkpoint)
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (none needed for CP1, but useful pattern to know)
# RUN apt-get update && apt-get install -y --no-install-recommends <pkg> && rm -rf /var/lib/apt/lists/*

# 1. Copy only the dependency manifest first (cache optimisation explained above)
COPY pyproject.toml .

# 2. Install dependencies
#    --no-cache-dir  → don't store pip's download cache inside the image (smaller image)
#    pip install ".[dev]" → installs runtime deps AND dev extras (ruff, pytest, httpx)
#
#    Why include dev deps in the image?
#    In a learning / development environment we want `make test` and `make lint`
#    to work inside the container without any extra steps.
#    In a production image you would use a multi-stage build and omit [dev].
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir ".[dev]"

# 3. Copy application source code
COPY app/ ./app/

# Expose the port uvicorn listens on (documentation only – actual binding via Compose)
EXPOSE 8000

# Start the app with uvicorn.
# We use shell form (not JSON array) so ${LOG_LEVEL} is expanded by the shell.
#   --host 0.0.0.0  → listen on all interfaces inside the container (required!)
#   --reload        → auto-restart on file changes (dev only; remove for production)
#   --log-level     → read from LOG_LEVEL env var injected by Compose, default "info"
CMD python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level ${LOG_LEVEL:-info}
