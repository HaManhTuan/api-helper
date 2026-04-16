# Research & decisions — Hanoi House Cleaning Booking API

**Feature**: `001-housemaid-booking-api` | **Date**: 2026-04-16

All items below were either **locked in parent `spec.md` (FR-043–045)** or **resolved** for planning so no **NEEDS CLARIFICATION** remains for contract design.

---

## 1. Quote before booking (FR-043)

**Decision**: Mandatory **two-step** API: `POST /quotes` → response includes **`quote_id`** → `POST /bookings` **must** include **`quote_id`**. Default quote validity **15 minutes**; reject if expired or pricing/catalog inputs drift beyond the stale threshold (see customer booking module edge cases).

**Rationale**: Single source of truth for customer-visible price before commit; avoids ambiguous “silent repricing” on create; aligns golden tests (SC-CC1).

**Alternatives considered**:

- **Single `POST /bookings` only** — rejected for initial API to keep server-side validation of a bound quote explicit.
- **Optional quote** — rejected; parent spec locks mandatory quote reference.

---

## 2. Helper KYC upload (FR-044)

**Decision**: **Presigned PUT** to object storage; MIME allowlist **`image/jpeg`, `image/png`, `application/pdf`**; **10 MiB** max per file; presigned URL TTL **15 minutes**; **`Content-Type`** on PUT must match declaration.

**Rationale**: Keeps large binaries off app servers; standard cloud pattern; clear failure mode (422) for bad MIME/size.

**Alternatives considered**:

- **Multipart straight to API** — rejected for v1 to avoid memory/timeout pressure and to match HLP-KYC-003 authorized URL pattern for reads.

---

## 3. Staff / Admin JWT (FR-045)

**Decision**: **Same issuer**, **same signing keys**, **same API base** as Customer/Helper. Claims: **`sub`**, **`roles`**, **`permissions`** (for Staff). **Admin** role = full internal access.

**Rationale**: One gateway, one token verification pipeline, simpler ops; matches FR-002/FR-003 RBAC story.

**Alternatives considered**:

- **Separate Staff IdP / service** — rejected for initial scope (explicitly out in FR-045).

---

## 4. Implementation stack

**Decision**: **Not specified** in this repo; consumers choose stack under constitution (lint, tests, performance validation).

**Rationale**: Repository is **documentation-first**; avoids blocking plan on language choice.

**Alternatives considered**: Pinning Laravel or Node — deferred to implementation repo README.

---

## 5. Stale quote vs price change

**Decision**: Follow **`customer-booking-creation-and-pricing.md`** edge case: **409** or **422** when quote invalid or totals diverge beyond threshold (exact threshold in implementation, default **reject** if delta &gt; configured %).

**Rationale**: Parent spec points to module for product policy; plan accepts **reject-stale** as default narrative.
