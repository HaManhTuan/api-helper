# Feature Specification: Helper — Reviews & Ratings (Received)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **xem** đánh giá từ khách (sau khi booking **completed**), **danh sách** review (có thể phân trang), và **rating tổng hợp** (`average_rating`, `count`) trên profile. Review bị Admin **ẩn** không hiển thị công khai cho Customer nhưng có thể vẫn hiện cho Helper với nhãn **hidden** — **policy** trong planning.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List reviews received (Priority: P1)

GET reviews where `helper_id = self`; sort mới nhất trước.

**Acceptance Scenarios**:

1. **Given** có review, **When** list, **Then** chỉ review của helper đó.
2. **Given** review moderated hidden, **When** helper xem, **Then** thấy flag **visibility** theo policy.

---

### User Story 2 - View aggregate on profile (Priority: P1)

Cùng số aggregate như Customer thấy (sau moderation) hoặc có thêm **internal count** — document in planning.

---

### Edge Cases

- **Không được phản hồi review** trong v1 (chat OOS) — optional future “response” field.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-REV-001**: Helper MUST **list** and **read** reviews **for self** only.
- **HLP-REV-002**: Helper MUST **read** aggregate rating on own profile consistent with `admin-reviews-moderation` visibility rules.
- **HLP-REV-003**: Helper MUST NOT create review for own service (chỉ Customer tạo review).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HR1**: Helper không đọc được review của helper khác (**403/404**).
