# Feature Specification: Helper — Authentication & Onboarding

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **đăng ký** và **đăng nhập** qua API công khai (cùng cơ chế JWT với Customer); sau đăng ký, trạng thái hồ sơ **pending approval** cho đến khi Admin duyệt (`admin-helper-moderation.md`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Helper registers (Priority: P1)

Helper đăng ký với role **Helper**, nhận xác nhận theo flow (email/SMS — planning). Tài khoản tạo ra với `approval_status = pending` (hoặc tương đương).

**Independent Test**: POST register helper → login → GET profile shows pending → cannot accept job.

**Acceptance Scenarios**:

1. **Given** payload hợp lệ, **When** register, **Then** user role Helper và profile ở trạng thái chờ duyệt.
2. **Given** Helper token **pending**, **When** accept booking, **Then** **403** với mã lý do rõ (e.g. `HELPER_NOT_APPROVED`).

---

### User Story 2 - Helper logs in and refreshes session (Priority: P1)

Login trả JWT; refresh/revoke nếu product hỗ trợ (giống Customer).

**Acceptance Scenarios**:

1. **Given** credentials đúng, **When** login, **Then** token có claim role Helper.
2. **Given** suspended helper, **When** login hoặc call API, **Then** **403** hoặc **401** theo policy.

---

### Edge Cases

- **Duplicate identifier**: email/phone đã tồn tại → **409** structured.
- **Switch role**: không cho phép self-elevate sang Admin.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-AUTH-001**: System MUST allow **registration** with role **Helper** và credentials có thể xác minh.
- **HLP-AUTH-002**: System MUST issue **JWT** cho Helper sau login; RBAC tách biệt Customer/Helper/Admin.
- **HLP-AUTH-003**: Helper **pending** hoặc **suspended** MUST NOT thực hiện **accept** booking (FR-010/011 enforcement).
- **HLP-AUTH-004**: Responses MUST use **structured errors** cho trạng thái không đủ điều kiện.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HA1**: **100%** negative tests: pending/suspended không accept được job.

## Assumptions

- **OTP/email verify** chi tiết trong planning; không đổi luồng nghiệp vụ Helper.
