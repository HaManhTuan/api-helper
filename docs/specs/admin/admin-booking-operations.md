# Feature Specification: Admin — Booking Operations & Oversight

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Parent feature: Admin **global** view of bookings, **filters**, **manual assign/reassign**, operational actions (e.g. cancel) within policy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin views all bookings with filters (Priority: P1)

An Admin opens a **global booking list** with filters: date range, status, customer id, helper id, district (if modeled), and pagination. Results include cross-tenant data **only** for Admin.

**Why this priority**: Operations center for the marketplace.

**Independent Test**: Seed bookings → Admin lists with status=pending → only matching rows; Customer token on same endpoint → 403.

**Acceptance Scenarios**:

1. **Given** bookings in multiple statuses, **When** Admin filters by **status**, **Then** only matching bookings are returned.
2. **Given** a date range filter, **When** Admin applies it, **Then** scheduled times (or created times—default in planning) fall within the range.
3. **Given** a Customer JWT, **When** calling admin global list, **Then** **403**.

---

### User Story 2 - Admin views a single booking detail (Priority: P1)

An Admin opens **booking detail**: customer, helper (if any), schedule, address, status history or timestamps, service type, cancellation/reassignment metadata **as available**.

**Why this priority**: Disputes and manual resolution require full context.

**Independent Test**: GET booking by id as Admin → 200; as unrelated Customer → 403/404.

**Acceptance Scenarios**:

1. **Given** a booking id, **When** Admin requests detail, **Then** response includes operational fields needed for support.
2. **Given** invalid id, **When** Admin requests detail, **Then** **404** structured error.

---

### User Story 3 - Admin manually assigns a helper to a pending booking (Priority: P1)

For a **pending** booking (often **no helper** or awaiting assignment), Admin selects an **eligible approved** helper and assigns. Per parent spec, default product rule: booking becomes **accepted** with that helper.

**Why this priority**: Fills gaps when automatic matching is weak.

**Independent Test**: pending booking + approved helper → admin assign → status **accepted**, helper set, audit log.

**Acceptance Scenarios**:

1. **Given** **pending** booking and eligible helper, **When** Admin assigns, **Then** booking shows **accepted** with helper and action is audit-logged.
2. **Given** helper not **approved** or **suspended**, **When** Admin assigns, **Then** **422/400** with structured reason.
3. **Given** booking not in assignable state, **When** Admin assigns, **Then** **409** or **422** per API rules.

---

### User Story 4 - Admin reassigns after helper release or dispute (Priority: P2)

When policy allows (e.g. helper cancelled, or admin overrides), Admin **clears** or changes helper and returns booking to **pending** (or equivalent) so another helper can take it—aligned with parent **reassignment** rules.

**Why this priority**: Avoids stuck bookings after helper failure.

**Independent Test**: accepted booking → reassign flow → pending + audit; second helper can accept.

**Acceptance Scenarios**:

1. **Given** booking in reassignable state per policy, **When** Admin reassigns, **Then** helper field and status update consistently and customers see updated state per parent Edge Cases.
2. **Given** concurrent helper accept after reassignment, **Then** race handling matches parent spec (one winner).

---

### User Story 5 - Admin cancels a booking when policy allows (Priority: P2)

In exceptional cases (double-booking, force majeure), Admin cancels a booking; **terminal** **cancelled** state; audit-logged. Conflicts with customer cancel rules must be documented.

**Why this priority**: Operational override beyond customer self-service.

**Independent Test**: Admin cancel → status cancelled → helper notified per policy (in-app only; push OOS).

**Acceptance Scenarios**:

1. **Given** a cancellable-by-admin booking, **When** Admin cancels with reason, **Then** status **cancelled** and audit log includes reason.

---

### Edge Cases

- **Double assignment**: Server prevents two helpers on same active booking except during controlled transition.
- **Timezone**: All schedule filters use a single documented timezone (e.g. **Asia/Hanoi**) in planning.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-BKG-001**: Admin MUST list **all** bookings with pagination and filters per planning.
- **ADM-BKG-002**: Admin MUST retrieve **booking detail** by id.
- **ADM-BKG-003**: Admin MUST **manually assign** helper to eligible **pending** bookings per parent status model.
- **ADM-BKG-004**: Admin MUST **reassign** per parent reassignment rules when permitted.
- **ADM-BKG-005**: Admin MAY **cancel** bookings per operational policy; MUST be audit-logged.
- **ADM-BKG-006**: All above endpoints MUST be **Admin-only**.

### Key Entities *(include if feature involves data)*

- **Booking**: As parent feature; admin views may include denormalized customer/helper labels for readability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-B1**: Filtered admin list returns correct subset in **100%** of contract tests for defined filter matrix.
- **SC-B2**: Manual assign and reassign each produce **audit** records with actor, booking id, helper id.

## Assumptions

- “Notify customer” of assignment change is via **app polling** or dashboard refresh; push notifications out of scope.
