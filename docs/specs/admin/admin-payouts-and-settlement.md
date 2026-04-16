# Feature Specification: Admin — Payouts, Settlement & Reconciliation

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: **Full** vòng đời **chi trả helper**: **kỳ** (tuần/tháng), **đối soát** booking đã completed, **tổng** phải trả, **trạng thái** `pending_approval → paid → failed`, **export** file ngân hàng (CSV), **ghi nhận** khi chưa có gateway (manual mark paid). **Platform fee** đã có trong snapshot; bảng này **tổng hợp** theo helper.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin generates payout batch (Priority: P1)

Chọn **kỳ**, hệ thống **tổng hợp** theo helper từ `BookingFinancialSnapshot` + **adjustments**; tạo **PayoutBatch** draft.

**Acceptance Scenarios**:

1. **Given** kỳ có N booking, **When** generate, **Then** batch **khớp** tổng line items.

---

### User Story 2 - Approval workflow (Priority: P1)

Role **finance** **approve** batch → **lock** → export **paid file** hoặc mark **paid**; **audit**.

---

### User Story 3 - Exception handling (Priority: P2)

Booking disputed sau khi đã batch → **clawback** hoặc **điều chỉnh kỳ sau** — rule trong planning.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-PAY-001**: System MUST support **payout batches** (create, list, approve, export, mark paid).
- **ADM-PAY-002**: Totals MUST **reconcile** với ledger/snapshot + adjustments.
- **ADM-PAY-003**: Permissions: `payouts:read`, `payouts:generate`, `payouts:approve`, `payouts:mark_paid` (matrix trong `admin-staff-and-roles`).
- **ADM-PAY-004**: All state transitions MUST audit-log.

### Key Entities

- **PayoutBatch**, **PayoutLine** (helper_id, amount, booking_ids summary).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-PY1**: **0** chênh lệch giữa batch total và sum ledger trong test suite.

## Assumptions

- **Chuyển khoản thực** qua file ngân hàng cho đến khi tích hợp gateway; **trạng thái paid** là **source of truth** nội bộ.
