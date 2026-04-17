#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env.prod}"
COMPOSE_FILE="${COMPOSE_FILE:-${ROOT_DIR}/docker-compose.prod.yml}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "[ERR] Missing ${ENV_FILE}"
  echo "Copy from .env.prod.example and update secrets first."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[ERR] docker is not installed"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "[ERR] docker compose plugin is not available"
  exit 1
fi

echo "[INFO] Using compose file: ${COMPOSE_FILE}"
echo "[INFO] Using env file: ${ENV_FILE}"

cd "${ROOT_DIR}"

echo "[INFO] Building production images..."
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" build

echo "[INFO] Starting services..."
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d

echo "[INFO] Running migrations..."
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T app poetry run python scripts/manage_migrations.py upgrade

echo "[INFO] Seeding default data..."
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" exec -T app poetry run python scripts/init_db.py

echo "[OK] Deployment completed."
echo "[INFO] Current service status:"
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps
