# Feature Specification: Helper — Profile & Service Area

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **đọc và cập nhật** hồ sơ: tên hiển thị, **kỹ năng / loại dịch vụ** (tags hoặc link tới `ServiceOffering`), **khu vực phục vụ** trong Hà Nội (quận/huyện hoặc polygon đơn giản — planning), bio ngắn. Một số trường có thể **read-only** sau khi Admin khóa.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Helper views and updates profile (Priority: P1)

GET/PUT profile; validation địa lý trong vùng **Hanoi** (parent spec).

**Acceptance Scenarios**:

1. **Given** approved helper, **When** update service_area, **Then** lưu thành công và ảnh hưởng matching (nếu có).
2. **Given** địa chỉ ngoài vùng cho phép, **When** save, **Then** **422** field errors.

---

### User Story 2 - Skills align with catalog (Priority: P2)

Helper chọn skills từ **service catalog** (ids) hoặc tags có kiểm soát — tránh text tự do không khớp giá.

**Acceptance Scenarios**:

1. **Given** invalid service id, **When** attach skill, **Then** **400/422**.

---

### Edge Cases

- **Admin lock**: Sau duyệt, một số field chỉ Admin sửa (flag `profile_locked`) — Helper GET thấy trạng thái.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-PRF-001**: Helper MUST **read** own **HelperProfile** (display, skills, service_area, approval_status, aggregate_rating read-only).
- **HLP-PRF-002**: Helper MUST **update** allowed fields per product rules; MUST validate **Hanoi** geography.
- **HLP-PRF-003**: Skills/service types MUST reference **catalog** where applicable (`admin-service-pricing-and-commission`).

### Key Entities

- **HelperProfile**: như spec tổng; `user_id`, `display_name`, `skills[]`, `service_area`, `approval_status`, `average_rating`, `ratings_count`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HP1**: Cập nhật hợp lệ phản ánh trong GET ngay sau save.
