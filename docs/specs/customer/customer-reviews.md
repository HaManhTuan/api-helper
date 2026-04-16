# Feature Specification: Customer — Reviews (Submit & View Own)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer gửi **một** đánh giá (sao + text tùy chọn) cho booking **completed** (FR-009); **không** gửi trùng; **xem** review đã gửi; không sửa sau X giờ nếu policy — optional.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit review (Priority: P1)

POST review sau completed; **duplicate** → **409**.

**Acceptance Scenarios**:

1. **Given** completed booking của mình, **When** submit, **Then** stored và helper rating cập nhật (sau moderation visibility — `admin-reviews-moderation`).
2. **Given** booking chưa completed, **When** submit, **Then** **422**.
3. **Given** booking của người khác, **When** submit, **Then** **403/404**.

---

### User Story 2 - List own submitted reviews (Priority: P2)

GET reviews **authored by self** (optional module).

---

### Edge Cases

- **Moderation**: review có thể **pending visibility** — customer thấy trạng thái “đang hiển thị” theo policy.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-REV-001**: Customer MUST **create** at most **one** review per **completed** booking (FR-009).
- **CUS-REV-002**: Customer MUST NOT review others’ bookings.
- **CUS-REV-003**: Customer MAY **list** own submitted reviews.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CR1**: Second POST review cùng booking → **409**.
