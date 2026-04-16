# AGENTS.md

Minimal operating guide for AI agents working in this repository.

## Source of truth and priority

When instructions conflict, apply this order:

1. `docs/specs/001-housemaid-booking-api/spec.md` and related files in `docs/specs/**`
2. `.cursor/rules/spec-alignment.mdc`
3. Other rules in `.cursor/rules/*.mdc`
4. Project skills in `.agents/skills/**/SKILL.md`
5. Generic/global skills only when not conflicting with project rules

## Always-follow implementation rules

- Read relevant `docs/specs/**` docs before implementing API or business logic.
- Keep architecture consistent: `controller -> service -> repository`.
- Keep controllers thin in `app/controllers/`; business logic in `app/services/`; data access in repositories.
- Use project response/error conventions (`ResponseBuilder`, structured errors).
- Enforce strict RBAC and role boundaries (`customer`, `helper`, `staff`, `admin`).
- Add/update tests for happy path and key error paths.
- Run `poetry run pre-commit run --all-files` for code-change tasks before finishing.

## Locked API guardrails (must comply)

- **FR-043**: Booking creation requires quote-first flow with valid `quote_id`.
- **FR-044**: Helper KYC uploads follow presigned upload contract (MIME/size/TTL constraints).
- **FR-045**: Staff/Admin auth follows the same JWT issuer/signing model and API base path.
- **FR-046**: Public API routes apply consistent rate limiting and structured `429` responses.
- **FR-047**: Use `403` for eligibility failure; reserve `422` for invalid payload semantics.

## Scope behavior

- Keep changes aligned to role/module scope in `docs/specs/{customer,helper,admin}/`.
- Do not introduce patterns that conflict with project rules/specs.
- If a request conflicts with specs, explicitly call it out and propose a compliant path.
