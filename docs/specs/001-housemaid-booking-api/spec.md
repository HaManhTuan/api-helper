# Feature Specification: Hanoi House Cleaning Booking API

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "Build an API server for a home cleaning (housemaid) booking platform in Hanoi. Backend-only for mobile app and admin dashboard. Roles: Admin, Helper, Customer. JWT auth, RBAC. Customer bookings, helper jobs, **full** admin operations (see `specs/admin/`). Booking status flow, reassignment. REST, validation, structured errors, admin action logging. Out of scope: **online payment gateway capture**, real-time chat, push notifications."

**Updated**: 2026-04-16 (Locked: FR-043–045; [`specs/README.md`](../README.md))

## Clarifications

### Session 2026-04-16

- Q: API public nên rate limit theo mô hình nào? → A: Theo IP + user token theo nhóm endpoint (Auth, Quote, Booking), có mã lỗi chuẩn khi vượt ngưỡng.
- Q: Khi quote còn tồn tại nhưng stale do thay đổi giá/rule thì trả response gì? → A: `409 Conflict`.
- Q: Luồng xử lý privacy request (export/delete/anonymize) là gì? → A: Customer gửi request; Admin/Staff duyệt và thực thi theo policy.
- Q: Retention mặc định cho booking completed là bao lâu? → A: Giữ tối thiểu 24 tháng, sau đó có thể anonymize theo policy.
- Q: Helper accept job nhưng không đủ điều kiện (KYC/insurance/approval) nên trả mã gì? → A: `403 Forbidden` cho eligibility fail; `422` chỉ cho payload sai.
- Q: Repeat customer rate theo tháng được định nghĩa thế nào? → A: Tỷ lệ customer của tháng M có thêm booking trong tháng M+1.
- Q: Mặc định xử lý privacy delete request là gì? → A: Anonymize dữ liệu nhận diện cá nhân; giữ bản ghi giao dịch/audit cần thiết.

## User Scenarios & Testing *(mandatory)*

This section describes **who** does **what**, under **which preconditions**, through **clear main and alternate flows**. Each user story is **independently testable** where possible; dependencies on other stories are called out explicitly.

### Scenario map

| Story | Actor | Primary outcome | Typical first step | Depends on |
|-------|--------|-----------------|--------------------|------------|
| US1 | Customer | A booking exists in Hanoi with correct details | Register / login as Customer | Modules [`specs/customer/`](../customer/README.md) |
| US2 | Helper | A job moves from offer/assignment to completed | Register / login as Helper; admin has approved helper (US3) for full E2E | US1 + modules [`specs/helper/`](../helper/README.md) |
| US3 | Admin | Platform is governable (users, bookings, analytics) | Login as Admin (internal account) | Chi tiết theo cụm: [`specs/admin/`](../admin/README.md) |
| US4 | Customer | Trust signal after service | Submit review after US1+US2 reach **completed** | US1, US2; [customer-reviews.md](../customer/customer-reviews.md) |

**Authentication note**: Every story assumes **JWT + RBAC** on protected actions. “Login” means obtaining a valid token for that role; **Admin never self-registers** on the public API.

---

### User Story 1 - Customer books and manages cleaning visits (Priority: P1)

**Summary**: A **Customer** in Hanoi registers (or logs in), obtains **quotes** (giá, VAT, khuyến mãi), creates booking requests (multi-line nếu có), views **only their** bookings with **financial breakdown**, and cancels when policy allows.

**Why this priority**: Booking is the core product outcome; without it the platform delivers no value.

**Customer module specifications** (see [`specs/customer/README.md`](../customer/README.md))

| Module | Spec |
|--------|------|
| Auth | [customer-auth-and-onboarding.md](../customer/customer-auth-and-onboarding.md) |
| Profile & địa chỉ | [customer-profile-and-preferences.md](../customer/customer-profile-and-preferences.md) |
| Tạo booking & báo giá | [customer-booking-creation-and-pricing.md](../customer/customer-booking-creation-and-pricing.md) |
| Lịch sử, chi tiết, hủy | [customer-booking-management-and-cancellation.md](../customer/customer-booking-management-and-cancellation.md) |
| Đánh giá | [customer-reviews.md](../customer/customer-reviews.md) |
| Chính sách (đọc) | [customer-policies-and-content.md](../customer/customer-policies-and-content.md) |
| Quyền dữ liệu | [customer-privacy-requests.md](../customer/customer-privacy-requests.md) |

**Preconditions**

- None for registration; for repeat use, a Customer account already exists.
- Booking address and time fall within **Hanoi** and validation rules (invalid input is rejected with structured errors).

**Main flow (happy path)**

1. Customer registers as **Customer** (or logs in).
2. Customer requests a **price quote** via the dedicated quote endpoint (**required**, FR-043), receives **`quote_id`**, then submits a **new booking** including that **`quote_id`** plus required fields: scheduled window, address, service type(s).
3. System creates booking with status **pending** (helper may be unassigned); **price snapshot** bound to the validated quote and admin rules.
4. Customer opens **booking history** and sees the new booking with current status và **breakdown** tiền.
5. If still allowed by status and **cancellation policy**, customer **cancels**; status becomes **cancelled**.

**Alternate / error flows**

- **A1 — Invalid data**: Missing field, outside Hanoi, or impossible time → request rejected; **no** booking created.
- **A2 — Cancel too late**: After cutoff or wrong status → cancel rejected with clear reason; booking unchanged.
- **A3 — Token missing or wrong role**: Protected endpoints return **401/403** with structured error (not a silent empty list).

**Acceptance scenarios (Given / When / Then)**

1. **Given** a Customer with a registered account and valid token, **When** they create a booking with all required fields inside Hanoi and a valid **`quote_id`**, **Then** the system persists a booking linked to that customer, returns a stable **booking id**, and initial status is **pending** (unless product assigns helper immediately).
2. **Given** a Customer with multiple bookings, **When** they list booking history, **Then** they see **only their** bookings, ordered by **most recent first** (created or scheduled—product default: **created_at** descending unless specified in planning).
3. **Given** a booking in **pending** or **accepted** (if policy allows cancel before work starts), **When** the customer cancels **before the cancellation cutoff** relative to scheduled start, **Then** status becomes **cancelled** and the booking is not actionable as active work for helpers.
4. **Given** a booking in **in-progress** or **completed**, **When** the customer attempts cancel, **Then** the system rejects cancel **or** routes to admin-only handling per policy (documented in planning—default: reject with reason).

**Independent test (how to verify this story alone)**

- Create Customer → create one valid booking → GET history shows it as **pending** → cancel within policy → GET shows **cancelled**.
- Assert another customer’s booking id is **not** visible in history (cross-tenant isolation).

---

### User Story 2 - Helper fulfills jobs and manages availability (Priority: P2)

**Summary**: A **Helper** registers (or logs in), sees **offered or assigned** bookings they are allowed to act on, **accepts or rejects**, moves work through **accepted → in-progress → completed**, updates **availability**, manages **KYC uploads** and **insurance visibility** where required, views **earnings** and **reviews**, and triggers **reassignment** when they cannot continue—without leaving bookings stuck.

**Why this priority**: Fulfillment turns requests into completed services.

**Helper module specifications** (see [`specs/helper/README.md`](../helper/README.md))

| Module | Spec |
|--------|------|
| Auth & onboarding | [helper-auth-and-onboarding.md](../helper/helper-auth-and-onboarding.md) |
| Profile & khu vực | [helper-profile-and-service-area.md](../helper/helper-profile-and-service-area.md) |
| Lịch rảnh | [helper-availability-schedule.md](../helper/helper-availability-schedule.md) |
| Booking & lifecycle | [helper-booking-offers-and-job-lifecycle.md](../helper/helper-booking-offers-and-job-lifecycle.md) |
| Thu nhập & payout (xem) | [helper-earnings-and-payouts-visibility.md](../helper/helper-earnings-and-payouts-visibility.md) |
| Đánh giá nhận được | [helper-reviews-and-ratings.md](../helper/helper-reviews-and-ratings.md) |
| KYC upload | [helper-documents-and-kyc-upload.md](../helper/helper-documents-and-kyc-upload.md) |
| Bảo hiểm (xem) | [helper-insurance-enrollment-view.md](../helper/helper-insurance-enrollment-view.md) |

**Preconditions**

- Helper account exists; for **accept new work**, helper profile is **approved** (not pending/suspended), và đủ **KYC/bảo hiểm** nếu policy yêu cầu.
- At least one **pending** booking exists (from US1 or test data) for end-to-end tests.

**Main flow (happy path)**

1. Helper logs in and lists bookings relevant to them (offered pool and/or “my jobs”).
2. Helper **accepts** a **pending** booking they are entitled to take → status **accepted**, booking linked to helper.
3. Helper sets status **in-progress** when work starts.
4. Helper sets status **completed** when done.
5. Helper maintains **availability** (recurring or dated windows); saves successfully.

**Alternate / error flows**

- **A1 — Reject offer**: Helper rejects → booking remains **pending**/unassigned or returns to pool per rules; **not** stuck without next state.
- **A2 — Cannot continue after accept**: Helper or system moves to **reassignment** or **cancelled** per policy; customer visibility of change is consistent with Edge Cases.
- **A3 — Unapproved / suspended helper**: Cannot accept new jobs; attempts return **403** with structured error.
- **A4 — Race**: Second helper accepts same booking → **one** wins; other gets **conflict** (e.g. 409) with clear message.

**Acceptance scenarios (Given / When / Then)**

1. **Given** an **approved** Helper, **When** they list bookings they may act on, **Then** the list excludes bookings that belong to other helpers’ exclusive assignments and excludes admin-only views.
2. **Given** a **pending** booking the Helper may claim, **When** they **accept**, **Then** the booking references this helper and status becomes **accepted** (or equivalent single “committed” state per status model).
3. **Given** an **accepted** booking for this Helper, **When** they update status to **in-progress** then **completed**, **Then** the customer’s view (US1) shows the same progression and **completed** unlocks review (US4).
4. **Given** a Helper defines or updates **availability**, **When** they save, **Then** persisted slots are returned on subsequent reads and can drive matching in later iterations (no payment/chat in scope).
5. **Given** two Helpers try to accept the **same** pending booking, **When** both submit accept, **Then** exactly one succeeds; the other receives a **conflict** response.

**Independent test (how to verify this story alone)**

- Seed or create **pending** booking + **approved** Helper → accept → in-progress → completed without DB hacks.
- Suspended helper token cannot accept new jobs.

---

### User Story 3 - Admin operates and governs the platform (Priority: P3)

**Summary**: An **Admin** (internal account only) signs in, **manages customers and helpers** (directory, approval, suspension), **oversees all bookings** (list, detail, manual assign/reassign, operational cancel), views **basic analytics**, and relies on a **queryable audit log** for accountability. Full coverage is split into **cluster specs** under [`specs/admin/`](../admin/README.md).

**Why this priority**: Trust, safety, and operability for a Hanoi marketplace.

**Preconditions**

- Admin user exists **outside** public self-registration.

**Admin cluster specifications (user stories by functional area)**

| Cụm | Spec | User stories (tiêu đề ngắn) |
|-----|------|-----------------------------|
| Staff & quyền | [admin-staff-and-roles.md](../admin/admin-staff-and-roles.md) | Nhiều tài khoản nội bộ; roles; permission matrix |
| Auth & truy cập | [admin-auth-and-access.md](../admin/admin-auth-and-access.md) | Login staff; MFA khuyến nghị; không public signup admin |
| Khách hàng | [admin-customer-accounts.md](../admin/admin-customer-accounts.md) | List/tìm; suspend; export/xóa theo policy |
| Helper | [admin-helper-moderation.md](../admin/admin-helper-moderation.md) | Duyệt, bulk, appeal; suspend/reinstate |
| KYC | [admin-helper-documents-kyc.md](../admin/admin-helper-documents-kyc.md) | Giấy tờ; duyệt; chặn nhận việc |
| Booking | [admin-booking-operations.md](../admin/admin-booking-operations.md) | Toàn hệ; gán/gán lại/hủy |
| Dịch vụ & giá | [admin-service-pricing-and-commission.md](../admin/admin-service-pricing-and-commission.md) | Catalog; giá/vốn; commission; multi-line; surge/vùng |
| Thuế & hiển thị | [admin-tax-vat-and-display.md](../admin/admin-tax-vat-and-display.md) | VAT; commission base |
| Khuyến mãi | [admin-promotions-and-vouchers.md](../admin/admin-promotions-and-vouchers.md) | Mã giảm; campaign |
| Bảo hiểm | [admin-insurance-and-risk.md](../admin/admin-insurance-and-risk.md) | Gói; enrollment; claim |
| Tranh chấp | [admin-disputes-and-adjustments.md](../admin/admin-disputes-and-adjustments.md) | Case; điều chỉnh nội bộ |
| Chi trả | [admin-payouts-and-settlement.md](../admin/admin-payouts-and-settlement.md) | Batch; approve; export; đối soát |
| Analytics | [admin-analytics.md](../admin/admin-analytics.md) | KPI; doanh thu/phí; **export** |
| Reviews | [admin-reviews-moderation.md](../admin/admin-reviews-moderation.md) | Kiểm duyệt đánh giá |
| Nội dung | [admin-content-and-policy.md](../admin/admin-content-and-policy.md) | Điều khoản, FAQ, version |
| Audit | [admin-audit-log.md](../admin/admin-audit-log.md) | Tra cứu; SIEM optional |

**Main flow (happy path — tổng quan E2E ops)**

1. **Staff** đăng nhập với token có **permissions** (clusters **staff/roles**, **auth**).
2. Admin maintains **service catalog**, **tax**, **pricing / commission**, **promotions** (clusters tương ứng); bookings support **multi-line** services.
3. **KYC** và **helper moderation**: duyệt giấy + hồ sơ; ghi nhận **insurance enrollment** nếu áp dụng.
4. **Booking ops**: danh sách toàn hệ; gán/gán lại; tranh chấp & **adjustments** khi cần.
5. **Payouts**: kỳ chi helper, batch, approve, export — đối soát với snapshot + adjustments.
6. **Analytics & export**: KPI, doanh thu nội bộ, file export.
7. **Reviews** moderation; **content/policy** publish.
8. Mọi thay đổi nhạy cảm → **audit** (và optional SIEM).

**Alternate / error flows**

- **A1 — Suspend helper or customer**: Target cannot use restricted capabilities; audit log entry exists.
- **A2 — Reassign**: Admin reassigns when permitted → booking state and helper fields consistent with parent status model; audit log entry exists.
- **A3 — Non-admin**: Customer/Helper token on admin routes → **403** + structured error.

**Acceptance scenarios (Given / When / Then) — umbrella checks**

1. **Given** a Helper in **pending approval**, **When** Admin approves, **Then** the helper may perform helper workflows (US2), and the action is **audit-logged** (see cluster specs for field-level AC).
2. **Given** an **approved** Helper, **When** Admin suspends them, **Then** they cannot accept **new** bookings, and suspension is **audit-logged**.
3. **Given** bookings from many customers, **When** Admin lists bookings with filters, **Then** results match filter criteria and include cross-customer data **only for Admin**.
4. **Given** a **pending** booking and an **eligible approved** Helper, **When** Admin manually assigns, **Then** booking shows **accepted** with that helper (product default: immediate acceptance) and assignment is **audit-logged**.
5. **Given** a date range with known test data, **When** Admin requests analytics, **Then** response includes **bookings per day** series and **active helpers** per definition in `admin-analytics.md`.

**Independent test (how to verify this story alone)**

- Chạy các **independent tests** trong từng file `specs/admin/*.md`; smoke test tổng: approve helper → assign booking → có bản ghi audit.

---

### User Story 4 - Post-service reviews and reputation (Priority: P4)

**Summary**: After a booking is **completed**, the **Customer** submits **one** star rating and optional text; **helper aggregate rating** updates for visibility to Admin and (if policy allows) Customers browsing helpers. Chi tiết: [`customer-reviews.md`](../customer/customer-reviews.md).

**Why this priority**: Quality and trust drive retention.

**Preconditions**

- Booking is **completed** for that customer and linked helper.
- Customer is the same person who created the booking.

**Main flow (happy path)**

1. Customer opens completed booking.
2. Customer submits rating (and optional comment).
3. System stores review and updates helper aggregates.

**Alternate / error flows**

- **A1 — Duplicate review**: Second POST for same booking → **rejected** (conflict or validation).
- **A2 — Too early**: Booking not **completed** → reject review.
- **A3 — Wrong customer**: Another customer’s booking id → **403/404** per security policy.

**Acceptance scenarios (Given / When / Then)**

1. **Given** a **completed** booking for this Customer, **When** they submit **one** review with valid rating, **Then** review is stored, linked to booking and helper, and duplicate submission is blocked.
2. **Given** multiple reviews for a Helper, **When** Admin or Customer views helper summary (per policy), **Then** **average rating** and **count** reflect stored reviews according to aggregation rules (e.g. simple mean of completed booking reviews).

**Independent test (how to verify this story alone)**

- Drive booking to **completed** (via US1+US2 or fixture) → POST review → GET booking shows review; helper summary shows updated aggregates.

---

### End-to-end scenario (cross-actor narrative)

**E2E — “First booking in Hanoi”** (uses US1–US4 in order):

1. **Customer** registers and creates booking → **pending**.
2. **Admin** approves **Helper** (if new) → helper can work.
3. **Helper** accepts booking → **accepted** → **in-progress** → **completed**.
4. **Customer** submits **review** → helper rating updates.

This narrative is a **traceability** check that stories connect (not a standalone deliverable).

---

### Edge Cases

- **Reassignment**: If a helper cancels after acceptance or becomes unavailable, the booking returns to a state where another helper can be assigned (manually by admin or per product rules). Customer is informed of material schedule or assignee changes.
- **Unassigned creation**: Bookings may be created without a helper; matching/assignment occurs afterward.
- **Cancellation cutoff**: Cancellations after the cutoff or in late stages may be disallowed or require admin handling; policy is configurable with a documented default.
- **Suspended or unapproved helpers**: Cannot accept new jobs; in-flight jobs follow a defined policy (complete vs reassigned).
- **Concurrent acceptance**: Two helpers must not accept the same pending booking; the system rejects conflicting updates clearly.
- **Invalid addresses or times**: Requests outside supported geography (Hanoi service area) or impossible schedules are rejected with structured, field-level feedback.
- **Admin accountability**: Sensitive admin actions (approval, suspension, manual assignment) are logged for audit.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance. Where a requirement conflicts with the constitution, resolve via
spec amendment or an explicit constitution update before implementation.

### Functional Requirements

#### Identity, authentication, and authorization

- **FR-001**: System MUST support registration and sign-in for **Customer** and **Helper** roles with credentials suitable for server-side verification (e.g. email or phone identifier—exact identifier strategy is an implementation choice if not fixed elsewhere).
- **FR-002**: System MUST issue authenticated sessions using **JWT** access tokens (and refresh or rotation strategy as needed) for API clients.
- **FR-003**: System MUST enforce **RBAC** so Customer, Helper, and Admin capabilities are separated; clients MUST NOT elevate role by tampering with tokens alone.
- **FR-004**: **Admin** accounts MUST be created and managed internally (not via public self-registration).
- **FR-005**: System MUST reject unauthorized access to role-protected operations with consistent, structured error responses.

#### Customer

Chi tiết theo module (`CUS-*`): [`specs/customer/README.md`](../customer/README.md).

- **FR-006**: Customers MUST be able to create booking requests with **date**, **time or time window**, **service location (address)**, and **service type** within the Hanoi service area; each create MUST include a valid **`quote_id`** from FR-043.
- **FR-007**: Customers MUST be able to list and view their own bookings and current status.
- **FR-008**: Customers MUST be able to cancel bookings **subject to cancellation rules** (cutoff before scheduled start, and status restrictions).
- **FR-009**: Customers MUST be able to submit **one review per completed booking** (rating + optional text) when eligible.
- **FR-042**: Customer-facing capabilities (auth, profile/addresses, quote & booking creation with pricing transparency, booking history/detail/cancel, reviews, published policies, privacy requests) MUST conform to `specs/customer/*.md` and stay consistent with admin commercial and content configuration.

#### Helper

Chi tiết theo module (`HLP-*`): [`specs/helper/README.md`](../helper/README.md).

- **FR-010**: Helpers MUST be able to view bookings available or assigned to them according to assignment state and eligibility.
- **FR-011**: Helpers MUST be able to **accept** or **reject** booking requests they are entitled to act on.
- **FR-012**: Helpers MUST be able to update job status along the defined flow: toward **accepted**, **in-progress**, and **completed**, and to signal inability to continue when rules require reassignment.
- **FR-013**: Helpers MUST be able to manage an **availability schedule** (recurring or dated windows) used for matching and display.
- **FR-041**: Helper-facing capabilities (auth, profile, availability, booking lifecycle, KYC upload, insurance read, earnings visibility, reviews read) MUST conform to the modules in `specs/helper/*.md` and remain consistent with admin policies (`specs/admin/`).

#### Admin

Chi tiết user story, acceptance criteria, và mã yêu cầu theo cụm (`ADM-*`): xem [`specs/admin/`](../admin/README.md).

- **FR-014**: Admins MUST be able to list and manage **users** (customers and helpers), including **approve** or **suspend** helpers.
- **FR-015**: Admins MUST be able to view **all bookings** with filters helpful for operations.
- **FR-016**: Admins MUST be able to **manually assign** or **reassign** helpers when business rules permit.
- **FR-017**: Admins MUST be able to retrieve **operational and financial analytics** (including at minimum **bookings per day**, **active helpers**, and **revenue/fee aggregates** per `admin-analytics.md`) for selected periods, with **export** support.
- **FR-018**: System MUST append **audit logs for administrative actions** (e.g. approval, suspension, manual assignment) suitable for troubleshooting and compliance review. **Staff** privileged actions (per `admin-staff-and-roles.md`) MUST be audited with the same rigor; actor identity is the **internal** user performing the action.
- **FR-028**: Admins MUST be able to configure a **service catalog** and **commercial rules**: customer **price**, **reference cost**, **margin**, and **commission split** (helper vs platform) per service or rule precedence, with **effective dating** where applicable (see `admin-service-pricing-and-commission.md`).
- **FR-029**: System MUST persist a **financial breakdown** on **completed** bookings (customer total, helper earnings component, platform fee component) derived from configured rules, for reporting; **live payment capture** remains governed by FR-025.
- **FR-030**: Admins MUST be able to configure **insurance products**, **helper enrollment** status, **claims** intake, and **assignment rules** that require active coverage when defined (see `admin-insurance-and-risk.md`).
- **FR-031**: System MUST support **multiple staff accounts** with **roles** and **fine-grained permissions** for admin operations (see `admin-staff-and-roles.md`).
- **FR-032**: Admins MUST be able to **moderate** customer reviews (hide, flag, recalculate aggregates) per `admin-reviews-moderation.md`.
- **FR-033**: Admins MUST be able to manage **dispute cases** and record **financial adjustments** linked to bookings for accounting and reconciliation (see `admin-disputes-and-adjustments.md`).
- **FR-034**: Admins MUST be able to configure **promotions and voucher codes** with deterministic stacking rules (see `admin-promotions-and-vouchers.md`).
- **FR-035**: Admins MUST be able to **verify helper KYC documents** and enforce document requirements before job acceptance (see `admin-helper-documents-kyc.md`).
- **FR-036**: Admins MUST be able to manage **policy content** (terms, FAQ, cancellation copy) with versioning and publish workflow (see `admin-content-and-policy.md`).
- **FR-037**: Admins MUST be able to configure **VAT/tax display rules** and commission tax-base semantics (see `admin-tax-vat-and-display.md`).
- **FR-038**: Admins MUST be able to run **payout batches**, approvals, and **reconciliation** with helper earnings (see `admin-payouts-and-settlement.md`).
- **FR-039**: Admins MUST be able to access **full analytics** including revenue/fee aggregates and **export** reports (CSV/XLSX or async jobs) per `admin-analytics.md`.
- **FR-040**: **Customers** MUST be able to submit and track **privacy requests** (export/delete/anonymize). **Admins/Staff** MUST review and fulfill these requests according to legal/compliance policy (see `admin-customer-accounts.md` and `customer-privacy-requests.md`); direct immediate self-service hard delete is out of scope. Default deletion handling is **anonymization** of personal identifiers while preserving required transaction/audit records.

#### Booking system and reviews

- **FR-019**: Every booking MUST reference a **customer**, optional **helper** at creation, **time slot**, **address**, **service type**, and **status** from the defined lifecycle.
- **FR-020**: System MUST support **reassignment** when a helper cancels or becomes invalid, returning the booking to a pool or pending assignment state per rules.
- **FR-021**: System MUST persist **reviews** tied to completed bookings and helpers, with aggregation for helper quality indicators.

#### API quality (non-functional, contract-level)

- **FR-022**: Public surface MUST follow a **RESTful** resource design with predictable collections and resource identifiers.
- **FR-023**: System MUST validate inputs and return **structured error responses** (machine-readable codes or fields plus human-readable messages) for client handling.
- **FR-024**: System MUST implement **consistent error handling** for validation, authorization, not-found, and conflict cases.
- **FR-046**: System MUST enforce **rate limiting** on public API routes using a combined policy of **IP-based** and **authenticated user-token-based** limits, with endpoint-group specific thresholds at minimum for **Auth**, **Quote**, and **Booking** flows; exceed events MUST return a consistent structured error (e.g., 429 + machine-readable code).
- **FR-047**: For Helper booking acceptance and similar eligibility-gated actions, server MUST return **403 Forbidden** when actor is authenticated but fails business eligibility (e.g., not approved, suspended, missing required KYC/insurance). **422 Unprocessable Entity** is reserved for syntactically/semantically invalid request payloads.

#### Explicitly out of scope (initial version)

- **FR-025**: **Payment gateway integration** (thu tiền thực qua cổng / ví điện tử) is **out of scope** for the initial backend unless explicitly added later. **In scope**: **full** admin **pricing**, **tax config**, **promotions**, **commission**, **ledger-style snapshots**, **payout batching/export**, **dispute adjustments**, **insurance workflows**, and related **reporting** as specified in `specs/admin/`.
- **FR-026**: Real-time chat is **out of scope**.
- **FR-027**: Push notifications are **out of scope** (may be added later).

#### Locked cross-cutting API decisions *(binding)*

These were previously left to planning; the following are **fixed** for contract design and QA.

- **FR-043 — Quote before booking (mandatory)**: Customers MUST obtain a **quote** via a **dedicated** endpoint (e.g. `POST /quotes`) **before** `POST /bookings`. The booking request MUST include **`quote_id`** (UUID returned by the quote). The server MUST reject booking creation if `quote_id` is missing, unknown, or **expired** (default **15 minutes** from quote creation). If `quote_id` exists but is **stale** under commercial rules (e.g. price/catalog changed beyond stale threshold), server MUST return **`409 Conflict`** with structured error code for stale quote. **Initial API**: no single-call booking that skips `quote_id` (clients may still run quote + confirm in one UI flow with two HTTP calls).
- **FR-044 — Helper KYC upload (presigned object)**: Helper document uploads MUST use **presigned PUT** URLs to object storage (S3-compatible or equivalent). **Allowed MIME types**: `image/jpeg`, `image/png`, `application/pdf` only. **Maximum object size**: **10 MiB** per file. **Presigned URL lifetime**: **15 minutes**. The client MUST send **`Content-Type`** on PUT matching the MIME type declared when the presigned URL was issued; mismatch MUST yield **422**. Admin/staff download or review URLs remain **short-lived authorized URLs** per module specs (HLP-KYC-003).
- **FR-045 — Internal Staff / Admin JWT (single issuer)**: **Staff** and **Admin** users MUST authenticate with JWTs from the **same issuer and signing configuration** as Customer and Helper tokens (FR-002), over the **same API base path** (no separate Staff-only auth service in initial scope). Access token claims MUST include **`sub`**, **`roles`** (e.g. `staff`, `admin`), and for **Staff**, a **`permissions`** array (string permission codes per `admin-staff-and-roles.md`). **Admin** role MUST denote **full** internal access ( **`permissions` optional or `["*"]`** — implementation choice; behavior MUST be equivalent to unconstrained admin). Authorization MUST be enforced server-side from verified claims; role elevation by client edits MUST fail at verification.

### Key Entities *(include if feature involves data)*

- **User**: Core identity, role (Customer, Helper, Admin, **Staff** with permissions), authentication factors, account status (active, suspended), timestamps.
- **Helper profile**: Skills/tags, service areas, approval state, aggregate rating, link to user, optional bio or experience fields for marketplace trust.
- **Booking**: Customer, optional helper, schedule (date/time window), address, service type(s) / **line items** when multi-service, status, cancellation/reassignment metadata, timestamps; optional **financial snapshot** when completed (price used, helper share, platform fee per rules).
- **SavedAddress** (Customer): Optional saved locations for faster booking (`customer-profile-and-preferences.md`).
- **Quote** (Customer): Ephemeral pricing result identified by **`quote_id`**, bound to inputs and TTL (FR-043); referenced by booking at creation.
- **Promotion / PriceBook / CommissionRule**: See admin commercial specs; referenced by quotes and snapshots.
- **PayoutBatch / PayoutLine**: Settlement (`admin-payouts-and-settlement.md`); Helper/Customer see **read-only** slices.
- **Dispute / DisputeAdjustment**: Customer-initiated or ops (`admin-disputes-and-adjustments.md`).
- **PrivacyRequest**: Customer-initiated; Admin fulfills (`customer-privacy-requests.md`, FR-040).
- **InsuranceProduct / Enrollment / Claim**: Admin-configured risk artifacts (`admin-insurance-and-risk.md`).
- **Review**: Booking reference, customer, helper, rating, text, created time, moderation state if needed.
- **Availability schedule**: Helper, recurrence or specific dates, time windows, enable/disable.
- **Admin audit log**: Actor (**Staff** or **Admin** user id), action type, target entities, timestamp, minimal context for investigations.

### REST API surface *(contract summary)*

Resources are **logical**; naming may be pluralized nouns. Authentication uses a standard `Authorization` header with bearer JWT for protected routes.

| Area | Typical operations |
|------|---------------------|
| Auth | Register (customer/helper), login, refresh token (if used), logout/revoke (if used), current user profile |
| Staff / Admin app | Internal users: JWT FR-045 + permissions (`admin-staff-and-roles`); **same API base** as other routes |
| Customer quote | Customer: **`POST /quotes` required** before booking; response includes **`quote_id`** (FR-043) |
| Customer privacy | Customer: submit/track data export or delete requests |
| Customer content | Customer/public: read published policies (terms, cancellation, FAQ) |
| Users / profiles | Get/update own profile; admin list/update users; admin helper approve/suspend |
| Bookings | Customer: **create with `quote_id`**, list own, get one, cancel; Helper: list relevant, get one, accept/reject, update status; Admin: list all, get one, assign/reassign |
| Availability | Helper CRUD on own schedule; admin read where needed |
| Helper earnings | Helper: read per-job and period earnings/payout status (read-only) |
| Helper KYC | Helper: upload/list own documents; Admin: verify |
| Reviews | Customer create review for completed booking; Helper read own received reviews; read on booking/helper as policy allows |
| Analytics | Admin: bookings-per-day series, active helpers count, date range query |
| Services & pricing | Admin: CRUD service offerings, price book entries, commission rules; multi-line; read catalog for quotes |
| Tax | Admin: VAT/display rules; tax lines on quotes |
| Promotions | Admin: promo codes; applied at quote |
| Staff | Admin: staff users, roles, permissions |
| Payouts | Admin: batches, approve, export, mark paid |
| Disputes | Admin: cases, adjustments |
| Content | Admin: policy pages, publish |
| Insurance | Admin: products, enrollment, claims; enforcement on assignment |

Exact paths and pagination/filter query names are finalized during planning; this table defines required capabilities.

### Data models *(logical)*

**User**

- `id`, `role`, `email` or `phone` (identifier), `status`, `created_at`, `updated_at`

**HelperProfile**

- `user_id`, `display_name`, `skills` (list), `service_area` (e.g. Hanoi districts or city-level), `approval_status` (pending, approved, suspended), `average_rating`, `ratings_count`

**Booking**

- `id`, `customer_id`, `helper_id` (optional), **`quote_id`** (FK to quote used at creation; immutable after create), `scheduled_start`, `scheduled_end` (or single slot), `address` (structured fields: line, district, city), `service_type`, `status`, `cancellation_reason` (optional), `created_at`, `updated_at`

**Quote** (logical)

- `id` (**`quote_id`**), `customer_id`, payload hash or serialized inputs, `expires_at` (default **15 minutes** after creation), `totals` / breakdown snapshot fields, `created_at`

**Review**

- `id`, `booking_id`, `customer_id`, `helper_id`, `rating` (bounded scale, e.g. 1–5), `comment`, `created_at`

**AvailabilitySlot**

- `id`, `helper_id`, `day_of_week` or `date`, `start_time`, `end_time`, `enabled`

**AdminAuditLog**

- `id`, `admin_user_id`, `action`, `entity_type`, `entity_id`, `metadata`, `created_at`

### Business rules

- **Service geography**: Bookings MUST be limited to **Hanoi** for the **initial product scope**; requests outside the defined area are rejected. Expansion to other locales is a **future** spec change.
- **Helper gating**: Only **approved** helpers may accept jobs; **suspended** helpers may not take new assignments.
- **One review per booking**: A customer may not submit multiple reviews for the same booking.
- **Rating window**: Reviews are allowed only after booking reaches **completed** (and within any stated time window—default: no expiry unless policy adds one later).
- **Cancellation**: Customers may cancel only in **allowed statuses** and before **cancellation cutoff** relative to scheduled start (default assumption: **24 hours** before start unless configured otherwise by admin policy).
- **Manual assignment**: Admins may assign when booking is in a state that permits assignment (typically **pending** or after helper release); reassignment follows the same status rules as automatic flows. Default product rule: admin assignment sets the booking to **accepted** with the chosen helper (helper-confirm step is optional if added in planning).
- **Admin logging**: Actions in FR-018 MUST be recorded with who/when/what for traceability.
- **Retention**: Completed booking records MUST be retained for a minimum of **24 months**; after that period data MAY be anonymized according to approved compliance policy while preserving required audit/accounting integrity.

### Status model

**Booking lifecycle**

1. **pending** — created; helper may be unassigned or assigned depending on product rules.
2. **accepted** — helper has committed (or admin assigned helper and helper acknowledged—plan may choose sub-states; externally visible status remains consistent with “accepted”).
3. **in-progress** — work underway.
4. **completed** — work finished; reviews allowed.
5. **cancelled** — terminal; no further progress except historical read.

**Transitions (allowed paths)**

- `pending` → `accepted` (helper accept or admin assign+accept rules) → `in-progress` → `completed`
- `pending` → `cancelled` (customer/admin per rules) or remain pending for reassignment
- `accepted` → `cancelled` (customer/admin/helper per rules) or → `in-progress`
- `in-progress` → `completed` or `cancelled` (policy-dependent; if helper aborts, move to reassignment or cancelled per rules)
- **Reassignment**: From `accepted` or `pending` when helper releases, return to a state where another helper can pick up (typically `pending` with cleared helper or explicit `awaiting_assignment`—implementation detail; behavior MUST match this spec).

Helpers **rejecting** a pending offer MUST NOT leave the booking stuck without a next state (remain pending/unassigned or notify admin per rules).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new customer can create an account and submit a valid booking in **one session** without staff assistance.
- **SC-002**: At least **95%** of syntactically valid booking submissions from test scenarios are accepted or rejected with **field-level reasons** (measured in QA against a defined form matrix).
- **SC-003**: Helpers can complete the flow from **pending** to **completed** for a booking in a test environment **without manual database edits**.
- **SC-004**: Admins can retrieve **bookings-per-day** and **active helpers** for an arbitrary **7-day** window in under **5 seconds** of user-perceived wait when querying typical volumes for a city-scale pilot.
- **SC-005**: **100%** of administrative actions covered by FR-018 produce an audit record within **1 minute** of the action in normal operation.
- **SC-006**: Monthly **repeat customer rate** MUST be computed as: from customers with at least one booking in month **M** (cohort base), count those with at least one booking in month **M+1**, divided by the cohort base for month **M**.

## Assumptions

- **Hanoi-only** service area for the **initial product scope**; addresses are considered valid if they meet defined city/district constraints in validation rules to be detailed in planning.
- **Identifier for login**: Email or phone is acceptable; OTP or email verification may be added in planning without changing core flows.
- **Matching algorithm**: May evolve from admin-heavy to automated matching; **configurable** rules in planning.
- **Cancellation default**: **24-hour** cutoff before scheduled start for customer-initiated cancellation unless product policy changes.
- **JWT**: Access tokens are short-lived; refresh strategy is defined in planning without changing RBAC outcomes. **Internal** Staff/Admin tokens follow **FR-045** (single issuer, same API base).
- **Clients**: Mobile app and admin dashboard consume this API; no web customer portal in scope beyond dashboard.
