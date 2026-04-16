# Feature Specification: Helper — Documents & KYC Upload

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **upload** tài liệu theo **loại** (CCCD, ảnh chân dung, sức khỏe…) — `storage_ref` sau upload an toàn; **theo dõi** trạng thái `pending_review / approved / rejected / needs_more_info`. Đối chiếu Admin: `admin-helper-documents-kyc.md`. **Chặn accept job** nếu thiếu doc bắt buộc đã duyệt.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload document (Priority: P1)

POST metadata + **presigned PUT** per parent **FR-044** (MIME/size/TTL); tạo record **pending_review**.

**Acceptance Scenarios**:

1. **Given** file hợp lệ, **When** upload, **Then** có record và status pending.
2. **Given** sai loại MIME/size (ngoài FR-044), **When** upload, **Then** **422**.

---

### User Story 2 - List own documents and status (Priority: P1)

GET documents for self only; không xem doc helper khác.

---

### User Story 3 - Blocked from jobs until required docs approved (Priority: P1)

Align **HLP-BKG** accept với `ADM-KYC` enforcement.

**Acceptance Scenarios**:

1. **Given** thiếu doc bắt buộc, **When** accept booking, **Then** **403** với code rõ.

---

### Edge Cases

- **Resubmit** sau **needs_more_info**: upload phiên bản mới, status pending lại.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-KYC-001**: Helper MUST **upload** and **list** own **HelperDocument** records only.
- **HLP-KYC-002**: System MUST enforce **required document** policy before **accept** (cross-ref FR + admin KYC).
- **HLP-KYC-003**: Download/view file MUST use **authorized** short-lived URL.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HK1**: **100%** negative tests: thiếu doc → không accept.
