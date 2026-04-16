# Feature Specification: Helper — Earnings & Payout Visibility (Read-Only)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Helper **xem** thu nhập theo từng job đã hoàn thành (từ **BookingFinancialSnapshot** — phần helper), **tổng theo kỳ** (tuần/tháng), và **trạng thái kỳ chi** (đã ghi nhận trong batch / đã thanh toán khi có quy trình — `admin-payouts-and-settlement`). Helper **không** chỉnh số tiền; không thay admin batch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View earnings per completed booking (Priority: P1)

GET earnings line hoặc embed trong booking detail khi **completed**: helper share, currency VND.

**Acceptance Scenarios**:

1. **Given** completed booking có snapshot, **When** helper xem, **Then** thấy **helper_earnings** khớp cấu hình commission.
2. **Given** booking chưa completed, **When** xem earnings detail, **Then** empty hoặc **404**.

---

### User Story 2 - View payout period summary (Priority: P2)

List **payout lines** liên quan helper: kỳ, số tiền, trạng thái (pending_payout / included_in_batch / paid — enum trong planning).

**Acceptance Scenarios**:

1. **Given** batch đã **paid**, **When** helper xem history, **Then** thấy record tương ứng.

---

### Edge Cases

- **Dispute adjustment**: sau điều chỉnh, helper thấy **revised** line hoặc note (policy).
- **FR-025**: không có cổng ví — helper vẫn thấy **số liệu nội bộ** và trạng thái **paid** khi ops đánh dấu.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **HLP-PAY-001**: Helper MUST **read** own **per-booking** helper earnings when snapshot exists.
- **HLP-PAY-002**: Helper MUST **read** own **payout history** / period summaries derived from settlement data (read-only).
- **HLP-PAY-003**: Helper MUST NOT modify financial records; **403** on write.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-HE1**: Số hiển thị cho helper **khớp** snapshot trong test seed.
