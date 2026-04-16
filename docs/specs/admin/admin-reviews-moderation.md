# Feature Specification: Admin — Reviews & Ratings Moderation

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin **kiểm duyệt** đánh giá: ẩn, gỡ, gắn cờ spam, điều chỉnh **hiển thị** aggregate rating khi có gian lận; hỗ trợ **khiếu nội dung** từ helper.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin lists reviews with filters (Priority: P1)

Lọc theo booking, helper, customer, khoảng sao, trạng thái **visible / hidden / flagged**, ngày.

**Acceptance Scenarios**:

1. **Given** review có nội dung vi phạm, **When** Admin **Hide**, **Then** khách không còn thấy trên app (helper vẫn thấy trong back-office nếu policy).

---

### User Story 2 - Admin overrides or recalculates aggregate (Priority: P2)

Khi có review bị ẩn, hệ thống **tính lại** `average_rating` và `count` theo quy tắc (chỉ visible) hoặc Admin ghi nhận **manual override** có audit.

**Acceptance Scenarios**:

1. **Given** hide review 5 sao, **Then** helper aggregate giảm đúng công thức.

---

### Edge Cases

- **Không xóa cứng** trừ khi policy pháp lý; mặc định **soft hide + audit**.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-REV-001**: Admin MUST list/filter reviews **toàn hệ**.
- **ADM-REV-002**: Admin MUST **hide/unhide** review và **flag** lý do.
- **ADM-REV-003**: Helper aggregate MUST **cập nhật** theo rule sau moderation (hoặc override có audit).
- **ADM-REV-004**: Actions MUST be audit-logged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-R1**: Sau hide, **0** hiển thị công khai trên API customer cho review đó.
