# Feature Specification: Admin — Staff Accounts, Roles & Permissions

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: **Full** operations: nhiều tài khoản nội bộ, **vai trò** (super admin, vận hành, tài chính, hỗ trợ, chỉ đọc…), **quyền** theo resource (users, bookings, pricing, payouts, audit…). Không chỉ một “Admin” đơn nhất.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Super admin provisions staff accounts (Priority: P1)

A **Super Admin** (hoặc break-glass) tạo tài khoản nhân viên, gán **role**, trạng thái **active/suspended**, và gửi **invite** hoặc đặt mật khẩu ban đầu theo quy trình nội bộ.

**Independent Test**: Tạo user ops → login → chỉ thấy API được phép.

**Acceptance Scenarios**:

1. **Given** Super Admin tạo staff với role **support**, **When** staff đăng nhập, **Then** không gọi được API chỉnh giá nếu policy từ chối.
2. **Given** staff bị **suspend**, **When** gọi API, **Then** **401/403** và có audit.

---

### User Story 2 - Role-based permission matrix (Priority: P1)

Hệ thống áp **permission matrix**: ví dụ `bookings:read:all`, `bookings:assign`, `pricing:write`, `payouts:approve`, `audit:read`, `staff:manage` (chỉ super). Thay đổi role hoặc permission **audit-logged**.

**Acceptance Scenarios**:

1. **Given** role **finance**, **When** gọi `POST /staff`, **Then** **403** trừ khi có quyền `staff:manage`.
2. **Given** cập nhật permission cho role, **Then** có bản ghi audit và hiệu lực **theo phiên hoặc request** (document policy).

---

### User Story 3 - Credential lifecycle (Priority: P2)

Đổi mật khẩu nội bộ, reset có quy trình (token một lần), **session revoke** (đăng xuất mọi thiết bị). Khuyến nghị **MFA** cho Super Admin và role có `payouts:approve` (mức bắt buộc do chính sách tổ chức).

**Acceptance Scenarios**:

1. **Given** admin reset password, **Then** session cũ vô hiệu nếu policy yêu cầu.

---

### Edge Cases

- **Không có role nào**: fallback **deny** (no implicit super).
- **Gỡ quyền đang đăng nhập**: request tiếp theo bị 403.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md` for code quality, testing,
UX consistency, and performance.

### Functional Requirements

- **ADM-STF-001**: System MUST support **multiple** staff accounts với **roles** và **permissions** có thể cấu hình (matrix hoặc enum mở rộng).
- **ADM-STF-002**: Chỉ role có chủ **staff management** (hoặc tương đương) **MUST** tạo/sửa/xóa tài khoản staff.
- **ADM-STF-003**: Mọi thay đổi role/permission **MUST** audit-log.
- **ADM-STF-004**: API **MUST** kiểm tra permission trên **mỗi** thao tác nhạy cảm, không chỉ dựa vào `role=admin` trong JWT nếu không đủ chi tiết.

### Key Entities

- **StaffUser**, **Role**, **Permission**, **RolePermission**, **StaffInvite** (optional).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-S1**: **100%** matrix test: mỗi role chỉ pass đúng tập API được thiết kế.

## Assumptions

- **SSO** (Google Workspace, Azure AD) là **optional** follow-up; spec này giả định email/password hoặc invite nội bộ.
