# Feature Specification: Admin — Disputes, Refunds & Commercial Adjustments

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: **Full** xử lý tranh chấp: ticket gắn booking, trạng thái, quyết định **goodwill**, **ghi nhận điều chỉnh** tài chính (credit/debit nội bộ) **không** bắt buộc cổng thanh toán — nhưng **đủ** để báo cáo và sau này đối soát payout.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin opens and tracks dispute case (Priority: P1)

Tạo **Dispute** từ booking: loại (chất lượng, thiệt hại, thanh toán…), mô tả, **status** `open → investigating → resolved → closed`, gán **owner** (staff).

**Acceptance Scenarios**:

1. **Given** booking completed, **When** mở dispute, **Then** liên kết booking + parties + audit.

---

### User Story 2 - Record financial adjustment (Priority: P1)

Admin ghi **adjustment**: ví dụ hoàn **X VND** cho khách (ghi nhận khi có gateway), hoặc **credit** nội bộ / **ghi có phí nền tảng** / **điều chỉnh helper** trong snapshot — **số dư kỳ** phản ánh trong báo cáo payout.

**Acceptance Scenarios**:

1. **Given** quyết định refund 50k, **When** lưu, **Then** có dòng adjustment gắn dispute + booking + audit.

---

### User Story 3 - Link to insurance claim (Priority: P2)

Dispute có thể **link** `InsuranceClaim` id nếu liên quan.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-DSP-001**: Admin MUST CRUD **dispute** cases với **workflow** trạng thái.
- **ADM-DSP-002**: Admin MUST ghi **financial adjustments** (amount, direction, reason code) gắn booking/dispute; **reconcile** với `BookingFinancialSnapshot` hoặc bảng ledger trong planning.
- **ADM-DSP-003**: Endpoints MUST respect **staff permissions** (`disputes:*`, `adjustments:*`).
- **ADM-DSP-004**: All actions MUST audit-log.

### Key Entities

- **Dispute**, **DisputeAdjustment**, optional link to **InsuranceClaim**.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-D1**: Mọi adjustment trong test **đối soát** với tổng báo cáo theo kỳ.

## Assumptions

- **Thực thu/chi** qua ngân hàng khi có gateway; trước đó **đủ sổ nội bộ**.
