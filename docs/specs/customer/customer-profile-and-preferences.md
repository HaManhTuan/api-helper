# Feature Specification: Customer — Profile & Saved Addresses

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer **đọc/sửa** hồ sơ hiển thị (tên, liên hệ); quản lý **địa chỉ đã lưu** (label “Nhà”, “VP”, địa chỉ đầy đủ trong Hà Nội) để chọn nhanh khi tạo booking.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update profile (Priority: P1)

GET/PUT `me` profile fields allowed.

**Acceptance Scenarios**:

1. **Given** valid data, **When** update, **Then** persisted.

---

### User Story 2 - CRUD saved addresses (Priority: P2)

Tạo/sửa/xóa địa chỉ; validate trong **service area** Hanoi.

**Acceptance Scenarios**:

1. **Given** address outside allowed area, **When** save, **Then** **422**.

---

### Edge Cases

- **Default address**: một địa chỉ default cho booking nhanh.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-PRF-001**: Customer MUST **read/update** own profile (no other user’s data).
- **CUS-PRF-002**: Customer MAY **manage saved addresses** với validation geography per parent spec.
- **CUS-PRF-003**: Endpoints MUST be **Customer-only** for write where applicable.

### Key Entities

- **CustomerProfile** / **User** extension; **SavedAddress**: id, label, line, district, city, lat/lng optional, is_default.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CP1**: Customer không đọc/sửa profile user khác (**403/404**).
