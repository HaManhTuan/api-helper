# Tasks: Hanoi House Cleaning Booking API (Business Delivery Version)

**Input**: Artifacts from `/specs/001-housemaid-booking-api/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

**Goal of this version**: Task descriptions are written in **business language** for delivery tracking.  
No code-level detail is required in task content.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel by different owners
- **[Story]**: User story mapping (`US1`, `US2`, `US3`, `US4`)

---

## Phase 1: Setup & Delivery Alignment

**Purpose**: Align scope, environments, and quality baseline before feature delivery.

- [ ] T001 Confirm delivery scope, assumptions, and out-of-scope boundaries with product and operations
- [ ] T002 Agree API release checklist (security, auditability, acceptance criteria, rollback approach)
- [ ] T003 [P] Establish shared glossary for statuses, pricing terms, and role permissions
- [ ] T004 [P] Define environment readiness checklist for dev/staging/prod
- [ ] T005 [P] Define evidence format for acceptance (test evidence, demo script, sign-off template)

---

## Phase 2: Foundational Business Capabilities (Blocking)

**Purpose**: Deliver cross-cutting capabilities required by all stories.

- [ ] T006 Finalize identity model for Customer, Helper, Staff, Admin and role boundaries
- [ ] T007 [P] Finalize JWT + permission behavior for internal users per FR-045
- [ ] T008 [P] Finalize structured error taxonomy and client-facing error handling policy
- [ ] T009 [P] Finalize audit policy for privileged actions per FR-018 (what must be logged, who can inspect)
- [ ] T010 [P] Finalize booking lifecycle and transition guardrails for all actors
- [ ] T011 [P] Finalize quote validity policy (TTL, stale behavior, rejection reasons) per FR-043
- [ ] T012 Finalize data retention and compliance baseline for booking, KYC, and privacy requests

**Checkpoint**: Foundation approved; story implementation can start.

---

## Phase 3: User Story 1 - Customer Booking Core (Priority: P1) 🎯 MVP

**Goal**: Customer can request quote, create booking with `quote_id`, manage own booking history, and cancel within policy.

**Independent Test**: New customer can complete quote -> booking -> history -> cancel flow without support.

### Validation tasks (US1)

- [ ] T013 [P] [US1] Validate quote-before-booking journey with success and failure scenarios
- [ ] T014 [P] [US1] Validate customer-only data isolation for booking list/detail
- [ ] T015 [P] [US1] Validate cancellation policy enforcement and clear rejection reasons

### Delivery tasks (US1)

**Role lane: Customer**

- [ ] T016 [P] [US1] Deliver customer onboarding and authenticated session behavior for booking use cases
- [ ] T017 [P] [US1] Deliver quote experience with transparent breakdown (base, tax, promotion, total)
- [ ] T018 [US1] Deliver booking confirmation flow bound to valid `quote_id`
- [ ] T019 [US1] Deliver booking history and booking detail visibility for customer only
- [ ] T020 [US1] Deliver cancellation flow with cutoff and status restrictions

**Role lane: Shared / Platform**

- [ ] T021 [P] [US1] Deliver operational visibility for failed quote/booking attempts
- [ ] T022 [US1] Deliver business-level error catalog for quote and booking scenarios
- [ ] T023 [US1] Deliver service-area enforcement for Hanoi-only booking acceptance
- [ ] T024 [US1] Deliver acceptance evidence pack for MVP sign-off

**Checkpoint**: US1 ready for MVP release.

---

## Phase 4: User Story 2 - Helper Fulfillment & Eligibility (Priority: P2)

**Goal**: Helper can receive/accept/reject jobs, update progress, manage availability, and comply with KYC constraints.

**Independent Test**: Approved helper can complete pending -> accepted -> in-progress -> completed flow; ineligible helper is blocked.

### Validation tasks (US2)

- [ ] T025 [P] [US2] Validate helper job lifecycle transitions and race conflict handling
- [ ] T026 [P] [US2] Validate helper eligibility gates (approval, suspension, KYC requirements)
- [ ] T027 [P] [US2] Validate KYC upload business constraints (allowed types, size, expiry handling)

### Delivery tasks (US2)

**Role lane: Helper**

- [ ] T028 [P] [US2] Deliver helper profile and readiness status for job acceptance
- [ ] T029 [US2] Deliver helper availability management aligned to matching needs
- [ ] T030 [US2] Deliver job offer handling (accept/reject) with clear outcomes
- [ ] T031 [US2] Deliver in-job progress updates and completion confirmation
- [ ] T032 [US2] Deliver helper visibility for earnings and received reviews

**Role lane: Staff/Admin + Helper cross-flow**

- [ ] T033 [US2] Deliver KYC submission journey with secure upload flow and status tracking
- [ ] T034 [US2] Deliver policy enforcement that blocks job acceptance when helper is ineligible

**Role lane: Shared**

- [ ] T035 [P] [US2] Deliver helper-side operational dashboard metrics for fulfillment health

**Checkpoint**: US2 independently operational.

---

## Phase 5: User Story 3 - Admin Governance & Operations (Priority: P3)

**Goal**: Internal users can govern platform operations, commercial rules, risk flows, and analytics with full auditability.

**Independent Test**: Admin can approve helper, assign booking, and retrieve audited action trail with valid analytics output.

### Validation tasks (US3)

- [ ] T036 [P] [US3] Validate internal authentication and permission-based access by staff/admin role
- [ ] T037 [P] [US3] Validate moderation operations (approve/suspend/reassign) with audit trace
- [ ] T038 [P] [US3] Validate commercial configuration impact on quote and booking outcomes
- [ ] T039 [P] [US3] Validate analytics report completeness and response-time target readiness

### Delivery tasks (US3)

**Role lane: Staff/Admin**

- [ ] T040 [P] [US3] Deliver internal login and permission governance per FR-045
- [ ] T041 [US3] Deliver staff role matrix and permission management lifecycle
- [ ] T042 [US3] Deliver customer/helper account moderation workflows
- [ ] T043 [US3] Deliver booking operations workflows (search, assign, reassign, operational cancel)
- [ ] T044 [US3] Deliver commercial controls (catalog, price, tax, commission, promotion)
- [ ] T045 [US3] Deliver KYC review and enforcement workflow for helper readiness
- [ ] T046 [US3] Deliver dispute, payout, insurance, content, and moderation operating capabilities
- [ ] T047 [US3] Deliver analytics and export operations for internal reporting

**Role lane: Shared / Compliance**

- [ ] T048 [P] [US3] Deliver governance playbook for sensitive operations and escalation
- [ ] T049 [US3] Deliver mandatory audit coverage verification for all privileged mutations

**Checkpoint**: US3 governable and auditable.

---

## Phase 6: User Story 4 - Reviews & Reputation (Priority: P4)

**Goal**: Customer can submit one review per completed booking; helper reputation updates; admin moderation controls visibility.

**Independent Test**: One completed booking accepts one review; duplicate blocked; moderation affects exposure correctly.

### Validation tasks (US4)

- [ ] T050 [P] [US4] Validate single-review rule and completed-booking eligibility
- [ ] T051 [P] [US4] Validate reputation aggregate behavior and moderation visibility policy

### Delivery tasks (US4)

**Role lane: Customer**

- [ ] T052 [US4] Deliver customer review submission flow with policy guardrails

**Role lane: Helper**

- [ ] T053 [US4] Deliver helper reputation view and review transparency rules

**Role lane: Staff/Admin**

- [ ] T054 [US4] Deliver review moderation actions and auditability

**Role lane: Shared**

- [ ] T055 [P] [US4] Deliver reputation integrity checks and anomaly monitoring

**Checkpoint**: US4 complete and policy-compliant.

---

## Phase 7: Polish & Release Readiness

**Purpose**: Ensure operational readiness across all delivered stories.

- [ ] T056 [P] Align contracts and user-facing behavior notes with delivered outcomes
- [ ] T057 [P] Deliver operations runbook (quote expiry, KYC failures, audit incident handling)
- [ ] T058 Validate quickstart and end-to-end demo script across all enabled stories
- [ ] T059 [P] Deliver security hardening checklist and sign-off
- [ ] T060 [P] Deliver release readiness review (quality gates, rollback plan, communication plan)

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 -> Phase 2 -> Story phases -> Phase 7
- Story phases can overlap after Phase 2 if owners are separated and dependencies are controlled

### User Story Dependencies

- **US1**: first MVP slice
- **US2**: depends on shared booking and policy foundation; E2E usually consumes US1 artifacts
- **US3**: governance lane can start early after foundation; full scope expands in later sprints
- **US4**: depends on completed booking flow and moderation policy

### Delivery Sprint Plan (Role-oriented)

#### Sprint 1 — US1 + Minimum Admin Governance

**In scope**: `T001`–`T024`, `T036`, `T040`, `T049`  
**Outcome**: MVP booking flow + internal access and audit baseline

#### Sprint 2 — Helper Fulfillment

**In scope**: `T025`–`T035` (+ regression on critical US1 flows)

#### Sprint 3 — Admin Full Ops + Reviews

**In scope**: remaining `T037`–`T048`, and `T050`–`T055`

#### Sprint 4 — Hardening

**In scope**: `T056`–`T060`

---

## Team Assignment Suggestion

- **Customer lane**: US1 + US4 customer tasks
- **Helper lane**: US2 tasks
- **Admin/Governance lane**: US3 tasks + moderation items
- **Platform/Compliance lane**: foundational, audit, release readiness

---

## Notes

- This file is intentionally business-oriented for delivery management.
- Story labels are retained for traceability with `spec.md`.
- Technical implementation details can be tracked separately in engineering tickets if needed.
