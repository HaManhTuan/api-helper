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

RESET  := \033[0m
BOLD   := \033[1m
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m

define print_info
	@printf "$(CYAN)$(BOLD)[INFO]$(RESET) %s\n" "$(1)"
endef

define print_success
	@printf "$(GREEN)$(BOLD)[OK]$(RESET) %s\n" "$(1)"
endef

define print_warn
	@printf "$(YELLOW)$(BOLD)[WARN]$(RESET) %s\n" "$(1)"
endef

define print_error
	@printf "$(RED)$(BOLD)[ERR]$(RESET) %s\n" "$(1)"
endef

.PHONY: help doctor env-check config build up down restart ps logs logs-app logs-worker \
	sh-app sh-db sh-redis app test test-cov lint precommit fmt migrate-up migrate-down \
	migrate-create migrate-history migrate-current migrate-up-local migrate-down-local \
	migrate-create-local migrate-history-local migrate-current-local db-init db-init-local \
	worker stop prune prod-config prod-build prod-up prod-down prod-logs prod-deploy

help: ## Show all available commands
	@printf "$(CYAN)$(BOLD)API Helper - Developer Makefile$(RESET)\n\n"
	@awk 'BEGIN {FS = ":.*## "; printf "$(BOLD)Usage:$(RESET) make <target>\n\n$(BOLD)Targets:$(RESET)\n"} /^[a-zA-Z0-9_.-]+:.*## / {printf "  $(GREEN)%-22s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

doctor: ## Verify required local tools
	@command -v docker >/dev/null || (printf "$(RED)docker not found$(RESET)\n"; exit 1)
	@docker compose version >/dev/null || (printf "$(RED)docker compose plugin not found$(RESET)\n"; exit 1)
	@command -v $(POETRY) >/dev/null || (printf "$(RED)poetry not found$(RESET)\n"; exit 1)
	$(call print_success,All required tools are available.)

env-check: ## Ensure environment file exists
	@test -f "$(ENV_FILE)" || (printf "$(RED)$(ENV_FILE) not found. Copy from .env.example first.$(RESET)\n"; exit 1)
	$(call print_info,Using env file: $(ENV_FILE))

config: env-check ## Validate and render docker compose config
	@$(COMPOSE) config >/dev/null
	$(call print_success,docker compose config is valid.)

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
	@test -n "$(MSG)" || (printf "$(YELLOW)Missing MSG. Example: make migrate-create MSG='add users table'$(RESET)\n"; exit 1)
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
	@test -n "$(MSG)" || (printf "$(YELLOW)Missing MSG. Example: make migrate-create-local MSG='add users table'$(RESET)\n"; exit 1)
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

prod-config: ## Validate production docker compose config
	@docker compose --env-file .env.prod -f docker-compose.prod.yml config >/dev/null
	$(call print_success,Production docker compose config is valid.)

prod-build: ## Build production docker images
	@docker compose --env-file .env.prod -f docker-compose.prod.yml build

prod-up: ## Start production stack in detached mode
	@docker compose --env-file .env.prod -f docker-compose.prod.yml up -d

prod-down: ## Stop production stack
	@docker compose --env-file .env.prod -f docker-compose.prod.yml down

prod-logs: ## Tail logs from production stack
	@docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail=200

prod-deploy: ## Build, start, migrate, and seed production stack
	@ENV_FILE=.env.prod COMPOSE_FILE=docker-compose.prod.yml ./scripts/deploy.sh
