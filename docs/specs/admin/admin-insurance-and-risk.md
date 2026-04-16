# Feature Specification: Admin — Insurance & Risk Configuration

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin **quản lý bảo hiểm** và rủi ro vận hành: gói bảo hiểm / mức phủ, điều kiện tham gia cho helper (hoặc nền tảng), trạng thái hợp lệ, và **vòng đời khiếu nại** ở mức nghiệp vụ (không thay thế tư vấn pháp lý). Tích hợp **cổng thanh toán** vẫn ngoài phạm vi parent; đây là **cấu hình và quy trình**.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin defines insurance products or coverage tiers (Priority: P1)

An Admin creates **insurance product** records tied to the marketplace (e.g. “Bảo hiểm trách nhiệm nghề nghiệp — gói A”, “Bảo hiểm tai nạn khi làm việc — gói B”). Fields include **name**, **coverage summary**, **validity period**, **eligibility rules** (e.g. only **approved** helpers), **premium model** (fixed per month / per job / included in platform fee — **config only** until billing exists), and **active** flag.

**Why this priority**: Helpers and customers need clarity on protection; ops needs structured data.

**Independent Test**: Create product → list → deactivate → new enrollments blocked per policy.

**Acceptance Scenarios**:

1. **Given** Admin creates a product with required fields, **When** saved, **Then** it is retrievable and referencable by id.
2. **Given** product is inactive, **When** enrollment is requested, **Then** system rejects with clear reason.
3. **Given** non-Admin, **When** writing products, **Then** **403**.

---

### User Story 2 - Admin tracks helper insurance enrollment status (Priority: P1)

For each helper, Admin can view **enrollment** into applicable products: **not_enrolled**, **pending**, **active**, **expired**, **revoked**. Admin **xác nhận** trạng thái sau khi đối chiếu giấy (workflow có thể kết hợp upload trong `admin-helper-documents-kyc.md`) và set **expiry date**.

**Why this priority**: Compliance and dispatch rules (“only insured helpers for premium tier jobs” — future rule).

**Independent Test**: Set helper H to **active** coverage until date D → status visible on helper admin view.

**Acceptance Scenarios**:

1. **Given** a helper and a product, **When** Admin records **active** enrollment with expiry, **Then** helper profile shows coverage state.
2. **Given** expiry in the past, **When** batch or read, **Then** status shows **expired** (or job scheduling warns per planning).

---

### User Story 3 - Admin handles incident / claim intake (Priority: P2)

When damage or injury is reported, Admin creates a **claim** record: booking reference, parties, description, severity, status **opened → under_review → closed** (accepted/rejected), optional **payout amount** (informational until finance integration). Attachments metadata (file ids) may be stored per planning.

**Why this priority**: Central place for risk events và **đủ** cho vận hành bảo hiểm end-to-end trên dashboard.

**Acceptance Scenarios**:

1. **Given** a valid booking id, **When** Admin opens a claim, **Then** claim is linked and audit-logged.
2. **Given** claim closed, **When** reopened, **Then** disallowed or requires new record per policy.

---

### User Story 4 - Risk rules for job assignment (Priority: P2)

Admin configures **whether certain service types require active insurance** (boolean per service or tier). Enforcement: booking creation or assignment **warns or blocks** if helper lacks coverage — exact strictness (**hard block vs soft**) fixed in planning.

**Why this priority**: Aligns commercial catalog with risk.

**Acceptance Scenarios**:

1. **Given** service S requires insurance, **When** helper without coverage is assigned, **Then** system **blocks** or **requires override with audit** per planning.

---

### Edge Cases

- **Legal**: Copy for policies is **admin-entered**; platform should disclaimer “not legal advice.”
- **Data privacy**: Claims may contain PII; access **Admin-only** and audit on view.
- **Cross-border**: N/A; Hanoi-only parent scope.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

- **ADM-INS-001**: Admin MUST manage **insurance product** definitions (CRUD, activate/deactivate).
- **ADM-INS-002**: Admin MUST record and view **helper insurance enrollment** status per product with effective dates.
- **ADM-INS-003**: Admin MUST create and update **claims** linked to bookings with a defined status workflow.
- **ADM-INS-004**: Admin MUST be able to configure **per service** whether **active insurance** is required for assignment (enforcement level in planning).
- **ADM-INS-005**: Insurance and claim endpoints: **write** Admin-only; **read** cho helper/customer **MAY** expose **tóm tắt phạm vi phủ** (policy-driven) qua API app — chi tiết trong planning.
- **ADM-INS-006**: Material changes (product, enrollment, claim resolution) MUST be **audit-logged**.

### Key Entities *(include if feature involves data)*

- **InsuranceProduct**: id, name, description, coverage_summary, premium_model enum, active, valid_from/to.
- **InsuranceEnrollment**: id, helper_id, product_id, status, effective_from, effective_to, notes.
- **InsuranceClaim**: id, booking_id, reporter_role, description, status, resolution_notes, amount_optional, created_at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-I1**: **100%** of claims created in integration tests retain linkage to booking and appear in admin list filter by status.
- **SC-I2**: Helper without required coverage cannot be assigned to restricted service in **100%** of negative tests when enforcement mode is **hard**.

## Assumptions

- **Issuing policies** is done with **external insurers** offline; system stores **metadata and status** only.
- **Premium collection** may be manual or future billing; not blocked by parent FR-025 if modeled as **accrual** only.
