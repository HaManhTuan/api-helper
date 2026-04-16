# Implementation Plan: Hanoi House Cleaning Booking API

**Branch**: `001-housemaid-booking-api` | **Date**: 2026-04-16 | **Spec**: [`spec.md`](spec.md)  
**Input**: Feature specification from `/specs/001-housemaid-booking-api/spec.md`

**Note**: Generated after locking **FR-043** (quote + `quote_id`), **FR-044** (KYC presigned upload), **FR-045** (Staff/Admin JWT) in the parent spec.

## Summary

Deliver a **REST backend** (implemented in a **separate application repository**; this repo holds **specifications only**) for a Hanoi-only home-cleaning marketplace: **Customer** and **Helper** mobile clients plus **Staff/Admin** dashboard, **JWT + RBAC**, full booking lifecycle, commercial rules (catalog, tax, promos, commission), admin ops (KYC, payouts, disputes, insurance, analytics), structured errors, and audit logging. **Online payment capture** remains out of scope (FR-025); **pricing snapshots and operational finance** are in scope.

**Locked contract decisions**: (1) **Quote-then-book** — `POST /quotes` then `POST /bookings` with **`quote_id`** and TTL/staleness rules (FR-043). (2) **Helper KYC** — presigned PUT, MIME whitelist, 10 MiB max, 15 min URL TTL (FR-044). (3) **Internal auth** — same JWT issuer and API base for Staff/Admin as for Customer/Helper (FR-045).

## Technical Context

**Language/Version**: **Python 3.12+** (FastAPI stack).  
**Primary Dependencies**: **FastAPI**, Pydantic v2, SQLAlchemy + Alembic, JWT auth library, Redis client, object storage SDK (presigned URLs).  
**Storage**: **PostgreSQL** (primary relational store), **Redis** (cache/ephemeral state), and object storage (S3-compatible) for KYC blobs.  
**Testing**: Implementation repo: unit + **contract/API tests** for REST + auth; integration tests for booking and quote flows; golden tests for pricing alignment (SC-CC1).  
**Target Platform**: Linux containers via **Docker** / managed container hosting.  
**Project Type**: **This repo**: specification + design artifacts only (`specs/`). **Consumer**: `web-service` (REST API).  
**Performance Goals**: Align with spec **SC-004** (admin analytics query ≤ **5 s** perceived wait for 7-day window at pilot volumes); API **p95** targets to be set in implementation (e.g. &lt; 300 ms for simple CRUD where practical).  
**Constraints**: Hanoi geography validation; RBAC isolation (no cross-customer reads); audit within **1 min** for FR-018 actions (SC-005); presigned URL and quote TTLs per FR-044 / FR-043.  
**Scale/Scope**: City-scale pilot; full admin surface per `specs/admin/`; no real-time chat or push (FR-026/027).

## Constitution Check

*GATE: Passed — design artifacts document testing strategy, performance touchpoints, and contract clarity. Re-checked after Phase 1.*

Aligned with `.specify/memory/constitution.md` (API Helper Docs):

- **Code quality**: Implementation PRs MUST keep diffs focused; lint/format in app repo.
- **Testing**: Contract tests for **quotes + bookings**, **403/401** matrix, quote expiry, KYC MIME rejection; integration for E2E US1–US4.
- **UX consistency**: Mobile/admin clients consume consistent error shape (FR-023/024); internal permissions follow `admin-staff-and-roles`.
- **Performance**: SC-004 and quote/KYC TTLs documented; load/DB indexing addressed in implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-housemaid-booking-api/
├── plan.md              # This file
├── research.md          # Phase 0 — resolved decisions
├── data-model.md        # Phase 1 — logical entities
├── quickstart.md        # Phase 1 — how to use artifacts
├── contracts/           # Phase 1 — REST contract index
└── tasks.md             # Phase 2 — from /speckit.tasks (not created here)
```

### Source Code (repository root)

This workspace **does not contain** application source. The implementation repository SHOULD follow a conventional layout, for example:

```text
api/
├── src/
│   ├── Http/            # controllers, requests, policies
│   ├── Domain/          # entities, booking/quote services
│   └── Infrastructure/ # DB, storage, JWT
└── tests/
    ├── Unit/
    ├── Integration/
    └── Contract/
```

**Structure Decision**: **Specs live under `specs/`** (including `admin/`, `customer/`, `helper/` modules). **Runtime code** lives in a separate repo or future directory; this plan governs **behavior and contracts**, not a monorepo layout here.

## Complexity Tracking

No constitution violations required for this documentation-only deliverable *(table not used)*.
