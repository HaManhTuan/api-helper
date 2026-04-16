# API Helper Fast

Backend API for a housemaid booking platform, built with FastAPI and layered architecture (`controller -> service -> repository`).

This project includes:
- JWT authentication and role-based access control (customer/helper/admin/staff)
- Staff RBAC matrix with common system-managed roles/permissions
- PostgreSQL + Alembic migrations
- Redis + Celery worker
- Docker-first local development flow

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- Poetry
- Docker Compose

## Quick Start (Docker - Recommended)

1. Copy environment file:

```bash
cp .env.example .env
```

2. Build images:

```bash
make build
```

3. Start services:

```bash
make up
```

4. Apply migrations:

```bash
make migrate-up
```

5. Initialize DB (seed common roles/permissions and default admin if needed):

```bash
make db-init
```

## Service Endpoints

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Postgres (host): `localhost:5433`
- Redis (host): `localhost:6379`

## Common Make Commands

### Docker lifecycle

```bash
make build
make up
make down
make restart
make ps
make logs
make logs-app
make logs-worker
```

### Shell into containers

```bash
make sh-app
make sh-db
make sh-redis
```

### Migrations / DB init (inside app container)

```bash
make migrate-up
make migrate-down
make migrate-create MSG="add something"
make migrate-history
make migrate-current
make db-init
```

### Local-only alternatives (non-docker)

```bash
make migrate-up-local
make migrate-down-local
make migrate-create-local MSG="add something"
make migrate-history-local
make migrate-current-local
make db-init-local
```

### Quality / tests

```bash
make test
make test-cov
make lint
make precommit
```

## Staff RBAC (Common Catalog)

Roles and permissions are system-managed common data (not created from current UI flow):

- Seed source: `app/config/staff_rbac.py`
- Seeded by: `scripts/init_db.py` / `make db-init`
- Related entities:
  - `roles`
  - `permissions`
  - `rolepermissions`
  - `staffauditlogs`
  - `users.staff_role_id`

Admin APIs for staff management live under `/api/v1/admin` and enforce permission checks from database source of truth.

## Project Structure

```text
api-helper-fast/
├── app/
│   ├── config/
│   ├── controllers/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── middlewares/
│   ├── utils/
│   └── workers/
├── alembic/
├── scripts/
├── docs/
├── tests/
├── docker-compose.yml
├── Dockerfile
└── Makefile
```

## Documentation

Main references:
- `docs/specs/001-housemaid-booking-api/spec.md`
- `docs/specs/admin/admin-staff-and-roles.md`
- `docs/development-guide.md`
- `docs/quick-reference.md`
- `docs/database_migrations.md`

## Notes

- Do not commit `.env`.
- For DataGrip local DB connection, use port `5433` (not `5432`) by default.
- `make migrate-*` commands are configured to run in the app container for consistent runtime behavior.
