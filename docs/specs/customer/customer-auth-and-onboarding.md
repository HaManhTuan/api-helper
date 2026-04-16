# Feature Specification: Customer — Authentication & Onboarding

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer **đăng ký** và **đăng nhập** (JWT); role **Customer**; tài khoản có thể **suspended** bởi Admin (`admin-customer-accounts.md`) — khi đó **403** trên thao tác nghiệp vụ.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Customer registers and logs in (Priority: P1)

Đăng ký với identifier (email/phone — planning); verify OTP/email nếu có; login trả JWT.

**Acceptance Scenarios**:

1. **Given** payload hợp lệ, **When** register Customer, **Then** user tồn tại với role Customer.
2. **Given** suspended Customer, **When** tạo booking, **Then** **403** với mã lý do.

---

### User Story 2 - Session lifecycle (Priority: P2)

Refresh token, logout/revoke nếu product hỗ trợ — nhất quán với Helper.

---

### Edge Cases

- **Trùng identifier**: **409**.
- **Không đăng ký Helper+Customer cùng email** — policy: một user một role hoặc tách — **fixed in planning** (default: một email một role).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-AUTH-001**: System MUST support **registration** và **login** cho role **Customer**.
- **CUS-AUTH-002**: System MUST issue **JWT** với role binding; RBAC tách Customer khỏi Helper/Admin.
- **CUS-AUTH-003**: **Suspended** customers MUST NOT create bookings hoặc submit reviews (structured **403**).
- **CUS-AUTH-004**: Structured errors cho **401/403**.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CA1**: **100%** blocked actions for suspended customer in negative matrix.

## Assumptions

- **Password reset / forgot** theo planning (email/SMS link).
