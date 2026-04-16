# Feature Specification: Customer — Policies & Published Content (Read)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer (và anonymous nếu cho phép) **đọc** nội dung đã **publish** từ `admin-content-and-policy`: điều khoản, chính sách hủy, FAQ, bảo mật — theo **locale** (vi/en) nếu có.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fetch policy by key (Priority: P2)

GET `/content/:key` hoặc tương đương; trả markdown/html + version + `updated_at`.

**Acceptance Scenarios**:

1. **Given** published content, **When** get, **Then** 200.
2. **Given** draft only, **When** public get, **Then** **404** hoặc last published.

---

### Edge Cases

- **Rate limit** public endpoints.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-CNT-001**: System MUST expose **read-only** access to **published** policy/content keys defined in admin CMS.
- **CUS-CNT-002**: Responses SHOULD include **version** for client cache invalidation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CCN1**: App luôn nhận bản **published** mới nhất theo locale.
