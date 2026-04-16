# Feature Specification: Customer — Booking History, Detail & Cancellation

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer **chỉ xem booking của mình** (FR-007); **lọc/sắp xếp**; **chi tiết** gồm trạng thái, helper gán (nếu có), lịch, địa chỉ, **breakdown giá** (subtotal, VAT, promo, tổng); **hủy** theo **cancellation policy** (FR-008). Theo dõi **reassign** (helper thay đổi) hiển thị rõ.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List and sort booking history (Priority: P1)

GET list: pagination; sort mặc định **created_at desc** (hoặc scheduled — planning); filter theo status optional.

**Acceptance Scenarios**:

1. **Given** nhiều booking, **When** list, **Then** chỉ `customer_id = self`.
2. **Given** booking id của customer khác, **When** detail, **Then** **404/403**.

---

### User Story 2 - View detail with financial summary (Priority: P1)

Detail bao gồm **status**, **helper** display nếu assigned, **timeline** trạng thái nếu có, **amounts** khớp snapshot.

---

### User Story 3 - Cancel booking (Priority: P1)

DELETE hoặc POST cancel theo API design; chỉ khi **allowed status** và **trước cutoff** (parent: default 24h).

**Acceptance Scenarios**:

1. **Given** pending + trong cutoff, **When** cancel, **Then** **cancelled**.
2. **Given** sau cutoff hoặc in-progress, **When** cancel, **Then** **409/422** với message.

---

### Edge Cases

- **Reassign**: customer thấy helper mới và lý do nếu policy hiển thị.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-MGT-001**: Customer MUST **list** và **view detail** **only own** bookings (FR-007).
- **CUS-MGT-002**: Customer MUST **cancel** subject to **rules** (FR-008); responses MUST be structured on denial.
- **CUS-MGT-003**: Detail MUST expose **price/tax/promo breakdown** consistent with booking snapshot for transparency.
- **CUS-MGT-004**: List/detail MUST NOT leak other customers’ data (**isolation tests**).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CM1**: **100%** isolation tests: không đọc booking người khác.
