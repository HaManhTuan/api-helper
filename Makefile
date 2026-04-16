SHELL := /bin/bash

ENV_FILE ?= .env
COMPOSE ?= docker compose --env-file $(ENV_FILE)

APP_SERVICE ?= app
DB_SERVICE ?= db
REDIS_SERVICE ?= redis
WORKER_SERVICE ?= celery_worker

POETRY ?= poetry
PYTHON ?= $(POETRY) run python

.DEFAULT_GOAL := help

.PHONY: help doctor env-check config build up down restart ps logs logs-app logs-worker \
	sh-app sh-db sh-redis app test test-cov lint precommit fmt migrate-up migrate-down \
	migrate-create migrate-history migrate-current migrate-up-local migrate-down-local \
	migrate-create-local migrate-history-local migrate-current-local db-init db-init-local \
	worker stop prune

help: ## Show all available commands
	@echo "API Helper - Developer Makefile"
	@echo ""
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

doctor: ## Verify required local tools
	@command -v docker >/dev/null || (echo "docker not found"; exit 1)
	@docker compose version >/dev/null || (echo "docker compose plugin not found"; exit 1)
	@command -v $(POETRY) >/dev/null || (echo "poetry not found"; exit 1)
	@echo "All required tools are available."

env-check: ## Ensure environment file exists
	@test -f "$(ENV_FILE)" || (echo "$(ENV_FILE) not found. Copy from .env.example first."; exit 1)
	@echo "Using env file: $(ENV_FILE)"

config: env-check ## Validate and render docker compose config
	@$(COMPOSE) config >/dev/null
	@echo "docker compose config is valid."

build: env-check ## Build/rebuild all docker images
	@$(COMPOSE) build

up: env-check ## Start stack in detached mode
	@$(COMPOSE) up -d

down: env-check ## Stop and remove containers/networks
	@$(COMPOSE) down

restart: down up ## Restart full docker stack

ps: env-check ## Show compose services status
	@$(COMPOSE) ps

logs: env-check ## Tail logs from all services
	@$(COMPOSE) logs -f --tail=200

logs-app: env-check ## Tail logs from app service
	@$(COMPOSE) logs -f --tail=200 $(APP_SERVICE)

logs-worker: env-check ## Tail logs from celery worker service
	@$(COMPOSE) logs -f --tail=200 $(WORKER_SERVICE)

sh-app: env-check ## Open shell in app container
	@$(COMPOSE) exec $(APP_SERVICE) /bin/bash

sh-db: env-check ## Open psql shell in db container
	@$(COMPOSE) exec $(DB_SERVICE) psql -U $$POSTGRES_USER -d $$POSTGRES_DB

sh-redis: env-check ## Open redis-cli in redis container
	@$(COMPOSE) exec $(REDIS_SERVICE) redis-cli

app: ## Run API locally (without docker)
	@$(POETRY) run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run all tests
	@$(PYTHON) scripts/run_tests.py

test-cov: ## Run pytest with coverage output
	@$(POETRY) run pytest --cov=app --cov-report=term-missing

lint: ## Run pre-commit checks on all files
	@$(POETRY) run pre-commit run --all-files

precommit: ## Install pre-commit hooks
	@$(POETRY) run pre-commit install

fmt: ## Format code via pre-commit formatters
	@$(POETRY) run pre-commit run --all-files

migrate-up: env-check ## Apply migrations inside app container
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/manage_migrations.py upgrade

migrate-down: env-check ## Roll back latest migration inside app container
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/manage_migrations.py downgrade

migrate-create: env-check ## Create migration inside app container (usage: make migrate-create MSG="add users table")
	@test -n "$(MSG)" || (echo "Missing MSG. Example: make migrate-create MSG='add users table'"; exit 1)
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/manage_migrations.py create -m "$(MSG)"

migrate-history: env-check ## Show migration history from app container
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/manage_migrations.py history

migrate-current: env-check ## Show current migration revision from app container
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/manage_migrations.py current

db-init: env-check ## Initialize DB and seed data inside app container
	@$(COMPOSE) exec $(APP_SERVICE) poetry run python scripts/init_db.py

migrate-up-local: ## Apply migrations locally (non-docker)
	@$(PYTHON) scripts/manage_migrations.py upgrade

migrate-down-local: ## Roll back latest migration locally (non-docker)
	@$(PYTHON) scripts/manage_migrations.py downgrade

migrate-create-local: ## Create migration locally (usage: make migrate-create-local MSG="...")
	@test -n "$(MSG)" || (echo "Missing MSG. Example: make migrate-create-local MSG='add users table'"; exit 1)
	@$(PYTHON) scripts/manage_migrations.py create -m "$(MSG)"

migrate-history-local: ## Show migration history locally (non-docker)
	@$(PYTHON) scripts/manage_migrations.py history

migrate-current-local: ## Show current revision locally (non-docker)
	@$(PYTHON) scripts/manage_migrations.py current

db-init-local: ## Initialize DB and seed data locally (non-docker)
	@$(PYTHON) scripts/init_db.py

worker: ## Start celery worker locally (without docker)
	@$(POETRY) run python scripts/start_worker.py

stop: env-check ## Stop services without removing containers
	@$(COMPOSE) stop

prune: ## Clean dangling docker artifacts (safe cleanup)
	@docker system prune -f
