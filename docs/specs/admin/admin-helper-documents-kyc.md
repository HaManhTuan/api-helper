# Feature Specification: Admin — Helper KYC & Document Verification

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper nộp **tài liệu** (CCCD, ảnh chân dung, giấy khám sức khỏe…); Admin **duyệt/từ chối/yêu cầu bổ sung**, lưu **metadata** file (storage implementation in planning), **không** lưu plaintext nhạy cảm không cần thiết.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Helper uploads documents (via API) (Priority: P1)

Helper gửi **document type** + file ref; trạng thái `pending_review`.

**Acceptance Scenarios**:

1. **Given** upload, **When** Admin mở queue, **Then** thấy theo helper, loại giấy.

---

### User Story 2 - Admin verifies or rejects (Priority: P1)

Chuyển **approved / rejected / needs_more_info**; lý do; **audit**.

**Acceptance Scenarios**:

1. **Given** CCCD chưa duyệt, **When** helper status approval cần KYC, **Then** block **accept job** until required docs **approved**.

---

### User Story 3 - Bulk review queue (Priority: P2)

Lọc theo ngày nộp, loại giấy; **bulk approve** khi đủ điều kiện (optional batch action).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-KYC-001**: System MUST support **document types** có cấu hình (admin).
- **ADM-KYC-002**: Admin MUST **review** documents với trạng thái và lý do.
- **ADM-KYC-003**: System MUST **enforce** policy: helper không thể **accept** booking nếu thiếu **required** doc approved (configurable per service tier).
- **ADM-KYC-004**: File access MUST be **authorized** (signed URL hoặc tương đương); **Admin-only** list raw files.
- **ADM-KYC-005**: All review actions MUST audit-log.

### Key Entities

- **HelperDocument**: helper_id, type, storage_ref, status, reviewed_by, reviewed_at.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-K1**: Negative test: thiếu doc bắt buộc → **100%** block accept.
