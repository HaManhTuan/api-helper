# Feature Specification: Helper — Availability Schedule

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper quản lý **lịch rảnh**: khung giờ theo **ngày cụ thể** và/hoặc **lặp theo tuần**; bật/tắt từng slot; không overlap không hợp lệ (validation).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Helper creates and lists availability slots (Priority: P1)

CRUD slot: `date` hoặc `day_of_week`, `start_time`, `end_time`, `enabled`.

**Acceptance Scenarios**:

1. **Given** slot không overlap sai, **When** save, **Then** persist và list trả về đúng.
2. **Given** overlap hoặc end ≤ start, **When** save, **Then** **422**.

---

### User Story 2 - Availability affects offer visibility (Priority: P2)

Khi matching engine tồn tại, booking offer chỉ hiện helper **available** tại slot (chi tiết engine trong planning).

**Acceptance Scenarios**:

1. **Given** helper không có slot cho thời điểm booking, **When** list offers (nếu rule bật), **Then** không thấy offer đó hoặc thấy với flag **outside_availability** — **deterministic** theo planning.

---

### Edge Cases

- **Timezone**: Asia/Hanoi.
- **Suspended helper**: có thể đọc lịch nhưng không nhận job mới.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-AVL-001**: Helper MUST **CRUD** own **availability** records only.
- **HLP-AVL-002**: System MUST **validate** time ranges và overlap rules.
- **HLP-AVL-003**: Admin MAY **read** helper availability (đã có admin-booking); Helper endpoints **Helper-only** write.

### Key Entities

- **AvailabilitySlot**: `helper_id`, `day_of_week` | `date`, `start_time`, `end_time`, `enabled`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HV1**: **100%** invalid overlap cases rejected trong contract tests.
