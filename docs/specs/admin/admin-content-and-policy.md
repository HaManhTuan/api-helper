# Feature Specification: Admin — Content, Policies & In-app Copy

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin chỉnh **nội dung chính sách** (FAQ, điều khoản, chính sách hủy, bảo mật), **bản dịch** (vi/en nếu có), **phiên bản**; **preview** trước publish; **hiển thị** qua API public read hoặc app embed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin edits policy page (Priority: P2)

CRUD **ContentBlock**: key (`terms`, `privacy`, `cancellation_policy`), locale, markdown/html, **version**, **published_at**.

**Acceptance Scenarios**:

1. **Given** publish draft, **When** app gọi `GET /content/cancellation_policy`, **Then** bản mới nhất **published**.

---

### User Story 2 - Version history (Priority: P3)

Lưu **history** mỗi lần publish; có thể **rollback** (super admin).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-CNT-001**: Admin MUST manage **content** keys và **locales**.
- **ADM-CNT-002**: MUST support **draft/publish** và **versioning**.
- **ADM-CNT-003**: Public read endpoints **MAY** không cần auth cho policy (rate-limited); **write** Admin-only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-C1**: App luôn nhận đúng bản **published** theo locale.
