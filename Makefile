# Makefile
# Convenience wrapper around docker compose commands.
#
# Why a Makefile?
#   - Short, memorable commands  (make up  vs  docker compose up --build -d)
#   - Single place to document the "official" way to run the project
#   - Works on Linux, macOS, and Windows (with GNU Make via WSL or choco install make)
#
# Usage: make <target>
# Run `make help` to list all targets.

COMPOSE = docker compose
BACKEND_SERVICE = backend

.PHONY: help up down logs shell test lint fmt build

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Build images and start all services in detached mode
	$(COMPOSE) up --build -d

down: ## Stop and remove containers and networks
	$(COMPOSE) down

logs: ## Tail logs from all services (Ctrl-C to stop)
	$(COMPOSE) logs -f

shell: ## Open an interactive bash shell inside the backend container
	$(COMPOSE) exec $(BACKEND_SERVICE) bash

test: ## Run pytest inside the backend container
	$(COMPOSE) exec $(BACKEND_SERVICE) python -m pytest app/tests -v

lint: ## Run ruff linter inside the backend container
	$(COMPOSE) exec $(BACKEND_SERVICE) python -m ruff check app

fmt: ## Run ruff formatter inside the backend container
	$(COMPOSE) exec $(BACKEND_SERVICE) python -m ruff format app

build: ## Build the backend Docker image only (no start)
	$(COMPOSE) build $(BACKEND_SERVICE)

ps: ## Show running containers
	$(COMPOSE) ps
