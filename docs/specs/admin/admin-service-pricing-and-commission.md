# Feature Specification: Admin — Service Catalog, Pricing & Commission

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin cấu hình **sâu** cho từng loại dịch vụ dọn dẹp: giá bán, giá vốn tham chiếu, biên lợi nhuận, **chia sẻ doanh thu** giữa nền tảng và helper (phần trăm / quy tắc). Tham chiếu mô hình **marketplace** (ví dụ: nền tảng giữ phí dịch vụ, đối tác nhận phần còn lại — tương tự tinh thần **Grab** / ride-hailing: **fare − platform fee = phần cho đối tác**), **không** bắt chước chi tiết sản phẩm bên thứ ba.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin defines cleaning service offerings (Priority: P1)

An Admin creates and maintains **service definitions** (e.g. “Dọn theo giờ”, “Dọn trọn gói”, “Vệ sinh kính”, add-on “thu gom rác”). Each offering has a stable **code**, **name**, **description**, **default duration or unit** (giờ, m², căn hộ), **active** flag, and optional **tags** for matching helpers.

**Why this priority**: Bookings reference service types; catalog is the root for pricing.

**Independent Test**: Create two services → list as Admin → Customer booking flow can reference service id (parent feature).

**Acceptance Scenarios**:

1. **Given** Admin creates a service with required fields, **When** saved, **Then** it appears in catalog and is version-addressable by id.
2. **Given** a service is **deactivated**, **When** Customer creates new booking, **Then** that service is not selectable (or shows deprecated per policy in planning).
3. **Given** non-Admin roles, **When** calling catalog write APIs, **Then** **403**.

---

### User Story 2 - Admin sets customer price, reference cost, and margin (Priority: P1)

For each service (or **variant** / **tier** — e.g. studio vs 3BR), Admin configures **customer-facing price** (the amount shown/charged in product terms), **reference cost** (ước tính chi phí gốc / COGS nội bộ), and derived **margin** (có thể lưu explicit hoặc tính từ server: `margin = price − reference_cost` per rules).

**Why this priority**: Commercial control and P&L visibility; **payment capture** remains a separate concern (parent FR-025).

**Independent Test**: Set price 200k, cost 120k → margin 80k or 40% per definition in planning.

**Acceptance Scenarios**:

1. **Given** valid numeric inputs, **When** Admin saves pricing row, **Then** system stores price, reference cost, and consistency rules pass (e.g. non-negative where required).
2. **Given** Admin updates price, **When** effective date rules apply, **Then** new bookings use new price after effective time (see US4).
3. **Given** invalid combinations (e.g. negative price), **When** save, **Then** structured validation errors.

---

### User Story 3 - Admin configures commission split (helper % vs platform %) (Priority: P1)

Admin defines **how revenue is split** for a completed job: e.g. **helper earns X%** of **customer price** (or of **price after tax line** — definition in planning), **platform retains Y%** as **service fee / commission**, and optional **fixed fee** per job. Totals MUST reconcile (e.g. X+Y = 100% of allocatable base, or explicit formula with rounding policy).

**Reference model (marketplace, Grab-like spirit)**:

- **Customer pays** quoted **fare / service price**.
- **Platform** takes **platform fee** (phần trăm hoặc cố định + %).
- **Helper** receives **partner earnings** = phần còn lại theo công thức đã cấu hình (compare: ride-hail “driver net” vs “platform fee”).

Exact formula MUST be documented in planning (single source of truth); spec requires **configurability** and **auditability**, not a specific payment rail.

**Independent Test**: Configure 75% helper / 25% platform on base price → completed booking produces **expected breakdown** in reporting objects; settlement qua `admin-payouts-and-settlement.md` khi chi thực.

**Acceptance Scenarios**:

1. **Given** a commission rule for a service, **When** a booking completes, **Then** stored **breakdown** shows helper share, platform share, and uses rounding rule (e.g. per-job round to 1 VND).
2. **Given** conflicting rules (overlap), **When** resolver runs, **Then** priority order is deterministic (e.g. service-specific overrides default).
3. **Given** non-Admin, **When** writing commission config, **Then** **403**.

---

### User Story 4 - Effective dates, zones, and surcharges (Priority: P1)

Admin **phải** có khả năng gắn **effective_from / effective_to** cho price và commission, **geography** (quận Hà Nội), **time-of-day** / **peak** multipliers (surge), **minimum job value**, và **fallback** khi không khớp vùng.

**Why this priority**: Real-world pricing varies by area and peak hours — **full** commercial ops.

**Acceptance Scenarios**:

1. **Given** two overlapping price versions, **When** booking is priced at time T, **Then** the **active rule** at T is selected by documented precedence.
2. **Given** peak multiplier 1.2x for weekend, **When** booking falls in window, **Then** customer price reflects multiplier before commission split (order of ops fixed in planning).

---

### User Story 5 - Audit and read-only history for commercial config (Priority: P1)

Every create/update/deactivate of catalog, price, or commission rule is **audit-logged** (who, when, before/after summary). Admin can **view history** or **export** per planning.

**Why this priority**: Disputes and finance reviews.

**Acceptance Scenarios**:

1. **Given** Admin changes helper % from 70 to 75, **When** saved, **Then** audit log entry exists with old/new values.
2. **Given** role **audit_read** (hoặc tương đương), **When** viewing history, **Then** entries are immutable.

---

### Edge Cases

- **Rounding**: VND integers; document **banker’s vs floor** for split remainder.
- **Partial completion / cancellation**: Split rules MUST support **cancellation policy** (deposit, partial service) theo cấu hình; snapshot booking phản ánh **partial** nếu có.
- **Tax/VAT**: Xem **`admin-tax-vat-and-display.md`**; commission base MUST follow **single** documented rule per service/global.
- **Multi-service booking**: Hệ thống **MUST** hỗ trợ **line items** (nhiều dịch vụ/add-on trên một booking): mỗi dòng có price + commission allocation hoặc **bundle rule** — quy tắc **precedence** ghi trong planning.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-PRICE-001**: Admin MUST manage **service catalog** (CRUD, activate/deactivate) for cleaning offerings.
- **ADM-PRICE-002**: Admin MUST configure per service (or variant): **customer price**, **reference cost**, and **margin** (stored or derived per rules).
- **ADM-PRICE-003**: Admin MUST configure **commission split**: **helper percentage and/or platform fee** (and optional fixed fees) with **reconciled** formulas.
- **ADM-PRICE-004**: System MUST compute and persist **per completed booking** a **financial breakdown** (customer price used, helper earnings, platform fee) for reporting; **actual payment settlement** may remain out of scope until gateway exists.
- **ADM-PRICE-005**: Pricing and commission rules MUST support **effective dating** and **precedence** rules documented in planning.
- **ADM-PRICE-006**: **Geography / peak / multiplier** rules MUST have **deterministic fallback** to default catalog price when no zone match.
- **ADM-PRICE-009**: System MUST support **multi-line** bookings (multiple services/add-ons) với **line-level** pricing và breakdown tổng hợp.
- **ADM-PRICE-007**: All changes to catalog or commercial rules MUST be **audit-logged** (aligned with `admin-audit-log.md`).
- **ADM-PRICE-008**: Commercial configuration APIs MUST be **Admin-only**.

### Key Entities *(include if feature involves data)*

- **ServiceOffering**: id, code, name, description, unit, active, metadata.
- **PriceBookEntry** (or similar): service_id, variant_id optional, customer_price, reference_cost, currency (VND), effective_from/to, zone_id optional.
- **CommissionRule**: service_id optional (default catch-all), helper_percent, platform_percent, fixed_platform_fee, fixed_helper_fee, effective_from/to, priority.
- **BookingFinancialSnapshot**: booking_id, customer_total, helper_payout_component, platform_fee_component, rule_ids applied, **line_items** optional, computed_at (for completed bookings).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-P1**: For **100%** of golden-path completed bookings in tests, **breakdown** sums match the configured formula within **1 unit** of currency after stated rounding.
- **SC-P2**: Admin can add a new service with full commercial fields in **under 10 minutes** in usability walkthrough (mock UI).

## Assumptions

- **Currency**: VND; **multi-currency** optional follow-up.
- **Payment gateway capture** remains **out of scope** per parent FR-025; **pricing, tax display, promotions, snapshots, payouts** are **in scope** as specified across `specs/admin/`.
- **Grab** is a **reference** for split semantics only; no third-party integration implied.
