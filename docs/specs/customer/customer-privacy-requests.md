# Feature Specification: Customer — Privacy & Data Subject Requests

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer **khởi tạo** yêu cầu **export** dữ liệu cá nhân hoặc **xóa/anonymize** tài khoản theo policy pháp lý; request vào **queue** xử lý bởi Admin (`admin-customer-accounts` FR-040); Customer **theo dõi** trạng thái request.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit data export request (Priority: P2)

POST request type `export`; nhận `request_id`, status `pending → processing → ready` + link download khi sẵn (TTL, signed URL).

**Acceptance Scenarios**:

1. **Given** authenticated customer, **When** request export, **Then** record created và audit.
2. **Given** ready, **When** download, **Then** one-time hoặc scoped access.

---

### User Story 2 - Submit delete/anonymize request (Priority: P2)

Workflow **pending approval** (Admin); có thể **từ chối** nếu có booking active — policy.

---

### Edge Cases

- **Identity verification** trước khi release export — **step-up** optional.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-PRV-001**: Customer MUST be able to **submit** privacy requests aligned with **FR-040** processing on admin side.
- **CUS-PRV-002**: Customer MUST **read** status of own requests only.
- **CUS-PRV-003**: System MUST NOT complete destructive delete without **admin workflow** when policy requires.

### Key Entities

- **PrivacyRequest**: id, user_id, type, status, created_at, resolution_notes (customer-visible summary).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CPV1**: Customer không thấy request của user khác.
