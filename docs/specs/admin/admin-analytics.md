# Feature Specification: Admin — Analytics, Dashboards & Exports

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: **Full** báo cáo vận hành và tài chính nội bộ: chỉ số theo thời gian, **doanh thu** (từ snapshot booking), **chi phí khuyến mãi**, **phí nền tảng**, **export** CSV/Excel (async nếu nặng), dashboard **tổng quan** và **cohort** cơ bản.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin views bookings per day (Priority: P1)

Admin chọn **date range** và nhận **time series**: số booking **created**, **completed**, **cancelled** (tách metric).

**Acceptance Scenarios**:

1. **Given** valid range, **When** query, **Then** buckets theo ngày (timezone **Asia/Hanoi**).
2. **Given** non-Admin, **Then** **403**.

---

### User Story 2 - Admin views supply and demand KPIs (Priority: P1)

**Active helpers**, **new registrations**, **accept rate**, **completion rate**, **median** thời gian phản hồi (nếu có timestamp).

**Acceptance Scenarios**:

1. **Given** seed data, **Then** KPI khớp định nghĩa trong API doc.

---

### User Story 3 - Revenue and take-rate reporting (Priority: P1)

Báo cáo **GMV**, **platform fee** tổng, **helper earnings** tổng (từ snapshot), có thể **group** theo dịch vụ / quận.

**Acceptance Scenarios**:

1. **Given** completed bookings, **When** revenue report, **Then** tổng khớp sum snapshots.

---

### User Story 4 - Export reports (Priority: P1)

Admin yêu cầu **export** (CSV/XLSX) cho báo cáo đã lọc; job **async** + **download link** khi sẵn sàng; **permission** `reports:export`.

**Acceptance Scenarios**:

1. **Given** export > N rows, **When** submit, **Then** **202** + poll URL; file có checksum metadata optional.

---

### User Story 5 - Cohort / retention (basic) (Priority: P2)

Tuần đầu **signup → booking** conversion; **repeat** customer rate theo tháng — định nghĩa cụ thể trong planning.

---

### Edge Cases

- **Large ranges**: pagination hoặc async export bắt buộc.
- **Timezone**: mọi chart dùng TZ đã cấu hình.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-ANL-001**: Admin MUST retrieve **time-series** và **aggregate** KPIs theo date range.
- **ADM-ANL-002**: Admin MUST retrieve **revenue / fee / helper earnings** reports derived from **booking financial data** (không cần gateway để báo cáo nội bộ).
- **ADM-ANL-003**: Admin MUST **export** tabular reports ở định dạng chuẩn (CSV tối thiểu; XLSX optional).
- **ADM-ANL-004**: Metrics endpoints MUST enforce **staff permissions** (không chỉ “is admin”).
- **ADM-ANL-005**: API MUST document **metric definitions** (reproducible).

### Key Entities

- **ReportExportJob** (optional): id, filters, status, file_ref, created_by.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-N1**: Cửa sổ **7 ngày** pilot: dashboard load **&lt; 5s** perceived với volume đã nêu ở parent SC-004.
- **SC-N2**: Export **100%** khớp cùng filter khi so với API JSON đồng điều kiện.

## Assumptions

- **BI** ngoài (Looker, Metabase) có thể **sync** qua export hoặc read replica — không bắt buộc trong spec API.
