# Feature Specification: Admin — Audit Log & Accountability

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Parent feature FR-018: **Audit logs** cho mọi hành động nhạy cảm — tra cứu, **immutable**, có thể **stream** tới SIEM (webhook optional).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System records audit entries for sensitive admin actions (Priority: P1)

Whenever an Admin performs covered actions (helper approve/suspend, customer suspend, manual assign/reassign, admin cancel, etc.), the system appends an **audit log** entry: **who** (admin user id), **when** (timestamp), **what** (action type), **targets** (entity type + ids), optional **metadata** (reason codes, before/after summary per planning).

**Why this priority**: Compliance, dispute resolution, and security accountability.

**Independent Test**: Perform each covered action in integration tests → assert one audit row per action with correct fields.

**Acceptance Scenarios**:

1. **Given** Admin approves a helper, **When** the action completes, **Then** an audit record exists with action type **helper_approve** (or equivalent) and target helper id.
2. **Given** Admin suspends a customer, **When** the action completes, **Then** audit record includes actor and customer id.
3. **Given** Admin assigns booking to helper, **When** the action completes, **Then** audit record links booking id and helper id.

---

### User Story 2 - Admin searches and filters audit log (Priority: P2)

An Admin opens an **audit log** view: filter by **date range**, **actor** (admin user), **action type**, **target entity** (booking, helper, customer). Results are paginated, sorted **newest first** by default.

**Why this priority**: Investigations require finding relevant events quickly.

**Independent Test**: Seed audit entries → filter by action type → subset matches.

**Acceptance Scenarios**:

1. **Given** multiple audit entries, **When** Admin filters by date range, **Then** only entries in range are returned.
2. **Given** non-Admin token, **When** requesting audit API, **Then** **403**.

---

### User Story 3 - Audit records are immutable (Priority: P1)

Existing audit records **cannot** be edited or deleted via API (**append-only**). Correction happens via **new** compensating entries nếu cần.

**Why this priority**: Trust in the audit trail.

**Independent Test**: No API updates audit row; attempts return **405** or are absent from OpenAPI.

**Acceptance Scenarios**:

1. **Given** an existing audit id, **When** a client attempts update/delete, **Then** operation is not supported.

---

### User Story 4 - Customers and helpers cannot read audit log (Priority: P1)

RBAC restricts audit endpoints to **Admin** only.

**Why this priority**: Prevents leaking operational details.

**Independent Test**: Customer/Helper GET audit → **403**.

---

### Edge Cases

- **Clock skew**: Timestamps stored in UTC with documented display TZ for Admin UI.
- **PII in metadata**: Avoid storing unnecessary PII; reason codes preferred over free text where possible.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-AUD-001**: System MUST persist **audit log entries** for all administrative actions listed in parent FR-018 and extended in admin cluster specs (approve, suspend, assign, reassign, cancel, reactivate, etc.).
- **ADM-AUD-002**: Each entry MUST include at minimum: **admin_user_id**, **timestamp**, **action**, **entity_type**, **entity_id(s)**, optional **metadata**.
- **ADM-AUD-003**: Admin MUST be able to **query** audit logs with filters and pagination per planning.
- **ADM-AUD-004**: Audit log read MUST be **Admin-only**.
- **ADM-AUD-005**: Audit records MUST be **append-only** (no update/delete via API).
- **ADM-AUD-006**: System **MAY** emit **webhook** hoặc file export cho SIEM (optional integration).

### Key Entities *(include if feature involves data)*

- **AdminAuditLog**: As parent feature logical model; field enumeration finalized in planning.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-D1**: **100%** of automated admin action tests assert a corresponding audit record (aligns with parent SC-005).
- **SC-D2**: **0** successful audit log reads by non-Admin roles in security test suite.

## Assumptions

- Long-term retention và archival là **ops/config**; API hỗ trợ **export** theo filter.
- **SIEM**: webhook **optional** (ADM-AUD-006).
