# Specifications index — Hanoi House Cleaning Booking API

**Feature root**: [`001-housemaid-booking-api/spec.md`](001-housemaid-booking-api/spec.md) — requirements **FR-001–FR-045**, status model, REST summary.

| Area | Path | Role / purpose |
|------|------|----------------|
| **Core (single file)** | [`001-housemaid-booking-api/spec.md`](001-housemaid-booking-api/spec.md) | End-to-end product: US1–US4, global FRs, lifecycle |
| **Admin (modules)** | [`admin/README.md`](admin/README.md) | Staff dashboard: `ADM-*` (commercial, ops, compliance) |
| **Helper (modules)** | [`helper/README.md`](helper/README.md) | Helper app: `HLP-*` |
| **Customer (modules)** | [`customer/README.md`](customer/README.md) | Customer app: `CUS-*` |
| **Quality checklist** | [`001-housemaid-booking-api/checklists/requirements.md`](001-housemaid-booking-api/checklists/requirements.md) | Spec quality iterations |

## Cross-cutting decisions (no conflict; resolve in planning)

1. **Identity**: One **role per user account** (Customer vs Helper) unless product explicitly allows linking later — [`customer-auth`](customer/customer-auth-and-onboarding.md) / [`helper-auth`](helper/helper-auth-and-onboarding.md) note.
2. **Admin vs Staff**: **Internal** users may be legacy “Admin” role or **Staff** with `ADM-STF-*` permissions; same API surface with RBAC — [`admin-staff-and-roles`](admin/admin-staff-and-roles.md). Audit actor = `staff_user_id` or `admin_user_id` per implementation.
3. **FR-018 audit**: Covers **privileged** actions by Admin **and** Staff (approve, pricing write, payout approve, etc.); extend entity naming in implementation, not duplicate requirements.
4. **Quote before booking**: **Locked** in parent spec (**FR-043**): dedicated **`POST /quotes`**, then **`POST /bookings`** with **`quote_id`** (TTL 15 min default). Module [`customer-booking-creation-and-pricing`](customer/customer-booking-creation-and-pricing.md) aligns with parent.
5. **FR-025**: Online **payment capture** out of scope; **pricing snapshots, payouts, disputes** in scope — đã nhất quán admin/customer/helper tài chính.
6. **Review visibility**: Admin moderation may **hide** reviews from **public** customer views; Helper/Customer modules đã nêu policy-driven visibility — implement một **visibility enum** chung.

## Verification log (2026-04-16)

- **FR numbering**: Continuous 001–027 (core), 028–040 (admin extension), 041–042 (helper/customer umbrellas) — **no duplicate IDs**.
- **Status model**: Single source in core `spec.md`; helper/customer modules align (**pending → … → completed/cancelled**).
- **Redundancy**: FR-041/042 **intentionally** summarize module dirs (traceability, not duplicate obligations).
