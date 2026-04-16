# Feature Specification: Admin — Helper Onboarding & Moderation

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Parent feature: Approve or suspend **helpers**, manage helper quality gates before they can accept jobs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin reviews pending helpers (Priority: P1)

An Admin opens a **queue** of helpers whose `approval_status` is **pending**, sees profile summary (skills, service area, identifiers), and decides **approve** or **reject** (rejection policy: helper cannot accept jobs until re-application or fix—defined in planning).

**Why this priority**: Unapproved helpers must not take paid work; trust anchor for the marketplace.

**Independent Test**: Register helper → appears pending → Admin approves → helper can accept booking in parent E2E.

**Acceptance Scenarios**:

1. **Given** a helper in **pending** approval, **When** Admin approves, **Then** `approval_status` becomes **approved** and the helper may accept jobs per parent rules; action is **audit-logged**.
2. **Given** a helper in **pending**, **When** Admin rejects (if supported), **Then** helper cannot accept jobs and outcome is audit-logged with reason code if applicable.
3. **Given** a non-pending helper, **When** Admin attempts duplicate approve, **Then** the system responds with a clear **409** or idempotent success per API design in planning.

---

### User Story 2 - Admin suspends or reinstates an approved helper (Priority: P1)

An Admin **suspends** an approved helper (quality issue, complaint, policy breach). Suspended helpers **cannot accept new bookings**; in-flight jobs follow parent **Edge Cases**. Admin may **reinstate** after review.

**Why this priority**: Ongoing safety and platform reputation.

**Independent Test**: Suspend helper → accept attempt returns **403**; reinstate → accept works again; audit trail complete.

**Acceptance Scenarios**:

1. **Given** an **approved** helper, **When** Admin suspends them, **Then** they cannot accept new assignments and suspension is audit-logged.
2. **Given** a **suspended** helper with an **in-progress** booking, **When** Admin or system applies policy, **Then** booking proceeds to completion or reassignment per parent spec (no orphaned state).
3. **Given** a suspended helper, **When** Admin reinstates, **Then** they may accept new work again and reinstatement is audit-logged.

---

### User Story 3 - Admin views helper profile for moderation (Priority: P2)

An Admin opens helper detail: profile fields, **aggregate rating**, approval status, optional recent reviews summary, availability summary **read-only** if needed for disputes.

**Why this priority**: Decisions require context beyond a single field.

**Independent Test**: GET helper as Admin → 200 with moderation-relevant fields; as Customer → limited fields per parent policy.

**Acceptance Scenarios**:

1. **Given** a helper id, **When** Admin requests detail, **Then** response includes moderation fields and excludes irrelevant secrets.
2. **Given** invalid id, **When** Admin requests detail, **Then** **404** structured error.

---

### User Story 4 - Helper cannot bypass approval (Priority: P1)

A **pending** or **suspended** helper token cannot accept bookings; server enforces **approval_status** on every accept path.

**Why this priority**: Security and business rule integrity.

**Independent Test**: Automated tests assert **403** on accept for pending/suspended regardless of client tampering.

**Acceptance Scenarios**:

1. **Given** helper status **pending**, **When** accept booking is attempted, **Then** **403** with structured reason.
2. **Given** helper status **suspended**, **When** accept is attempted, **Then** **403**.

---

### Edge Cases

- **Appeal flow**: Helper có thể **yêu cầu xem xét lại** (ticket) → Admin xử lý; trạng thái gắn helper profile.
- **Bulk approve**: Admin **MAY** approve hàng loạt từ queue (permission + audit).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-HLP-001**: Admin MUST be able to list helpers filtered by **approval_status** (at least pending, approved, suspended).
- **ADM-HLP-002**: Admin MUST be able to **approve** pending helpers and **reject** pending applications if the workflow supports rejection.
- **ADM-HLP-003**: Admin MUST be able to **suspend** and **reinstate** helpers; enforcement MUST apply to all accept/job paths.
- **ADM-HLP-004**: Admin MUST be able to **view** helper profile/detail for moderation.
- **ADM-HLP-005**: Approve, reject, suspend, reinstate MUST be **audit-logged** per parent FR-018.

### Key Entities *(include if feature involves data)*

- **HelperProfile**: `approval_status` (pending, approved, suspended), skills, service_area, aggregate_rating, link to User.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-H1**: **100%** of acceptance tests block **pending** and **suspended** helpers from job acceptance.
- **SC-H2**: Every state transition (approve/suspend/reinstate) in integration tests has a matching **audit** record with actor and target.

## Assumptions

- Helper **registration** creates **pending** approval by default.
- Rejection may leave account in a terminal “rejected” state or allow resubmission—exact enum in planning.
