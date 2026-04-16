# Feature Specification: Admin — Customer Account Directory

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Parent feature: Admins manage **customers** — search/list, view profile summary, suspend or reactivate accounts for fraud or policy violations.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin searches and lists customers (Priority: P1)

An Admin opens the customer directory with **pagination**, optional **search** (email/phone/name per planning), and sees a list of customers with key fields (identifier, status, created date).

**Why this priority**: Support and trust operations require finding users quickly.

**Independent Test**: Seed customers → Admin lists with filter by status → results match seed data only for Admin token.

**Acceptance Scenarios**:

1. **Given** several customer accounts, **When** Admin requests the customer list, **Then** the response is paginated and contains only **Customer** role users.
2. **Given** a search string matching one customer, **When** Admin searches, **Then** results include that customer and exclude non-matches.
3. **Given** a Helper or Customer token, **When** they call the admin customer list endpoint, **Then** the system returns **403**.

---

### User Story 2 - Admin views customer detail (Priority: P1)

An Admin opens a **customer profile** view: identity fields, account status, high-level booking counts or recent activity summaries **as defined in planning** (without exposing secrets).

**Why this priority**: Investigation and support need a single place to understand account state.

**Independent Test**: GET customer by id as Admin → 200 with profile; as another Customer → 403/404 per policy.

**Acceptance Scenarios**:

1. **Given** a valid customer id, **When** Admin requests detail, **Then** the response includes role-appropriate fields and **no** password or raw secrets.
2. **Given** a non-existent id, **When** Admin requests detail, **Then** the system returns **404** with structured error.

---

### User Story 3 - Admin suspends or reactivates a customer account (Priority: P2)

An Admin **suspends** a customer to block new bookings and logins (per policy), or **reactivates** after review. Suspension MUST be **audit-logged** (see `admin-audit-log.md`).

**Why this priority**: Fraud and abuse handling without deleting historical data.

**Independent Test**: Suspend customer → customer token cannot create booking → reactivate → can book again; audit entries exist.

**Acceptance Scenarios**:

1. **Given** an active customer, **When** Admin suspends the account, **Then** subsequent customer actions (login or booking) are denied per policy and action is audit-logged.
2. **Given** a suspended customer, **When** Admin reactivates, **Then** the customer regains normal capabilities and reactivation is audit-logged.

---

### User Story 4 - Admin cannot impersonate customer session without explicit scope (Priority: P3)

Unless a separate “support impersonation” feature is approved later, Admin actions are **explicit** (suspend, view) and do **not** silently inherit customer JWT.

**Why this priority**: Clear security boundary; avoids confused-deputy issues.

**Independent Test**: No endpoint returns a customer JWT to Admin without a dedicated future spec.

**Acceptance Scenarios**:

1. **Given** Admin token, **When** calling standard admin APIs, **Then** responses do not include secrets that enable full session takeover of the customer unless a future spec defines it.

---

### Edge Cases

- **GDPR / local law**: Admin **MUST** có luồng **export dữ liệu cá nhân** (machine-readable) và **yêu cầu xóa** theo policy pháp lý (workflow + audit) — chi tiết SLA trong planning.
- **Concurrent suspend**: Last write wins; server enforces current status on each request.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-CUST-001**: Admin MUST be able to **list** and **search** customers with pagination and filters aligned to planning.
- **ADM-CUST-002**: Admin MUST be able to **view** customer profile/detail for support, excluding sensitive secrets.
- **ADM-CUST-003**: Admin MUST be able to **suspend** and **reactivate** customer accounts; effects on login and booking MUST match documented policy.
- **ADM-CUST-004**: Customer directory endpoints MUST be **Admin-only** (RBAC).
- **ADM-CUST-005**: Suspension and reactivation MUST generate **audit log** entries per parent feature FR-018.
- **ADM-CUST-006**: Admin MUST support **data export** và **delete/anonymize request** workflow per legal policy (permissions: `users:privacy`).

### Key Entities *(include if feature involves data)*

- **User (Customer)**: `id`, identifiers, `status` (active/suspended), timestamps.
- **Customer metrics (optional view model)**: Counts of bookings by status—detail level in planning.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-C1**: Admin locates a target customer from a list of **500+** test users via search in **under 30 seconds** of operator time in usability testing (mock data).
- **SC-C2**: After suspension, **100%** of blocked actions in the agreed test matrix fail until reactivation.

## Assumptions

- **Delete / anonymize** customer: **in scope** qua quy trình Admin có **approval** và **audit** (soft-delete vs hard-delete theo policy).
- Customer booking history detail from Admin view may be a **summary** with link to booking ops spec for full list.
