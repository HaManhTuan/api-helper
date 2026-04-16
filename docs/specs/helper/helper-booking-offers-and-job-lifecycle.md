# Feature Specification: Helper — Booking Offers & Job Lifecycle

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper xem **booking mở** (offer pool) và **job đã gán cho mình**; **accept** / **reject**; chuyển trạng thái **accepted → in-progress → completed**; **release** job để **reassign** khi không tiếp tục được (theo policy); xử lý **race** khi hai helper cùng accept.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List offers and my jobs (Priority: P1)

Hai danh sách (hoặc filter): **available offers** (pending, chưa gán hoặc trong pool) và **my jobs** (helper = self). Không lộ booking của helper khác.

**Acceptance Scenarios**:

1. **Given** approved helper, **When** list offers, **Then** chỉ booking đủ điều kiện (địa lý, skill, insurance, KYC — enforcement từ planning).
2. **Given** list my jobs, **Then** chỉ booking có `helper_id = self`.

---

### User Story 2 - Accept booking (Priority: P1)

POST accept trên booking pending; chuyển **accepted**, gán helper; nếu conflict → **409**.

**Acceptance Scenarios**:

1. **Given** booking pending và helper đủ điều kiện, **When** accept, **Then** status **accepted**, helper set.
2. **Given** helper khác đã accept, **When** accept, **Then** **409** + structured error.
3. **Given** thiếu KYC/bảo hiểm bắt buộc, **When** accept, **Then** **403/422** theo `admin-helper-documents-kyc` / insurance rules.

---

### User Story 3 - Reject offer (Priority: P1)

Reject không gán helper; booking quay **pending** pool hoặc tương đương — **không** stuck.

---

### User Story 4 - Update job status (Priority: P1)

**accepted → in-progress → completed**; không nhảy trạng thái sai thứ tự.

**Acceptance Scenarios**:

1. **Given** accepted, **When** start work, **Then** **in-progress**.
2. **Given** in-progress, **When** complete, **Then** **completed** và unlock review phía Customer.

---

### User Story 5 - Release / cannot continue (Priority: P2)

Helper báo **cannot_complete** hoặc **release** → booking vào trạng thái **reassign** (pending pool) hoặc **cancelled** theo policy; **audit**; customer thấy cập nhật (parent Edge Cases).

---

### Edge Cases

- **Concurrent accept**: một thắng, một thua — **409**.
- **Admin manual assign**: helper thấy job đã **accepted** với mình ngay (parent rule).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-BKG-001**: Helper MUST list **relevant** bookings (offers + assigned) per FR-010.
- **HLP-BKG-002**: Helper MUST **accept** or **reject** eligible pending bookings per FR-011.
- **HLP-BKG-003**: Helper MUST **update status** theo lifecycle per FR-012 và parent status model.
- **HLP-BKG-004**: Helper MUST be able to **signal release/reassign** when policy allows, without orphan bookings.
- **HLP-BKG-005**: System MUST return **409** on lost race for accept.
- **HLP-BKG-006**: Helper MUST **get detail** một booking chỉ khi **authorized** (assigned self hoặc offer visible).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HB1**: E2E: pending → accepted → in-progress → completed với một helper approved.
- **SC-HB2**: **0** successful double-accept trong concurrency test.
