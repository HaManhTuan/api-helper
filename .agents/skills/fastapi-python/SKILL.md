---
name: fastapi-python
description: FastAPI backend implementation aligned with this repository's architecture and conventions
---

# FastAPI Python

Implement FastAPI backend code according to this project's existing architecture.

## Project-First Principles

- Follow project rules in `.cursor/rules/` first.
- Treat `docs/specs/001-housemaid-booking-api/spec.md` as the business-contract source of truth.
- Keep architecture consistent: `controller -> service -> repository`.
- Reuse base abstractions before creating custom logic:
  - `BaseService[Model, Repository]`
  - `FullRepositoryImpl[Model]`
- Keep domain boundaries clear and avoid duplicated logic.

## Required Conventions (This Repository)

- Controllers are in `app/controllers/`, use `APIRouter`.
- Business logic lives in `app/services/`.
- Data access lives in `app/repositories/concrete/`.
- Schemas are split by domain in `app/schemas/{domain}/` with `request.py`, `schema.py`, `converters.py`, `__init__.py`.
- API responses must use `ResponseBuilder.success()` / `ResponseBuilder.error()`.
- Use type hints and Pydantic schemas for all external inputs/outputs.

## Error Handling

- Raise project-specific exceptions for business failures.
- Let middleware handle generic/HTTP exception shaping.
- Handle only domain-specific exception branches in controllers when necessary.
- Use guard clauses and explicit validation paths.

## FastAPI Guidelines

- Use `async def` for I/O-bound endpoints and repository/service operations.
- Keep route handlers thin: parse input, call service, format response.
- Use dependency injection (`Depends`) for auth/session/service dependencies.
- Keep startup/shutdown concerns in lifespan/middleware layers.

## Spec-Locked Behavior

- Require `quote_id` for booking creation and handle stale quotes with `409` where applicable.
- Use `403` for authenticated eligibility failures; use `422` for invalid payload semantics.
- Keep Staff/Admin auth on same JWT issuer and API base as Customer/Helper.
- Implement structured rate-limit responses (`429`) on public endpoint groups.

## Logging and Quality Gates

- Use `get_trace_logger()` consistently.
- Prefer non-blocking I/O and async database calls.
- After changes, run `poetry run pre-commit run --all-files`.

## When Not to Use This Skill

- Do not use as a generic starter template that changes project structure.
- Do not introduce alternative architectures that conflict with `.cursor/rules/architecture.mdc`.

## Stack Assumptions

FastAPI, Pydantic, SQLAlchemy (async), Poetry-managed tooling.
