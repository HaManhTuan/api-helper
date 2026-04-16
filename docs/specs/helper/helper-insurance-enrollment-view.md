# Feature Specification: Helper — Insurance Enrollment (Read & Actions)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **xem** trạng thái tham gia bảo hiểm (theo sản phẩm platform): **not_enrolled**, **pending**, **active**, **expired**; **tóm tắt phạm vi** (text từ admin config). Có thể **acknowledge** điều khoản hoặc **upload bằng chứng** phí nếu quy trình yêu cầu — chi tiết workflow **Admin-driven** (`admin-insurance-and-risk`). Helper **không** tự sửa trạng thái **active** (Admin ghi nhận).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View enrollment status (Priority: P2)

GET insurance enrollment summary cho self.

**Acceptance Scenarios**:

1. **Given** Admin đã ghi **active** đến ngày D, **When** helper xem, **Then** thấy ngày hết hạn.

---

### User Story 2 - Booking blocked without coverage (Priority: P1)

Khi service yêu cầu insurance (`admin-insurance`), accept job **403** nếu không **active**.

**Acceptance Scenarios**:

1. Align với **HLP-BKG-002** và **ADM-INS-004**.

---

### Edge Cases

- **Claim**: Helper có thể **báo sự cố** qua flow riêng (POST incident) nếu product mở — có thể nằm booking support; tối thiểu **link** tới hotline trong content.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-INS-001**: Helper MUST **read** own **insurance enrollment** summary per product.
- **HLP-INS-002**: System MUST **enforce** insurance requirement on **accept** when configured.
- **HLP-INS-003**: Helper MUST NOT set enrollment to **active** without Admin workflow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HI1**: Helper không đọc enrollment của helper khác.
