# Feature Specification: Customer — Booking Creation & Pricing (Quote)

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Customer **chọn dịch vụ** (catalog), **time slot**, **địa chỉ** (Hà Nội), optional **add-ons / multi-line**; nhận **báo giá** (subtotal, VAT, promotion, **tổng**) trước khi xác nhận; **POST** tạo booking **pending**. Khớp `admin-service-pricing`, `admin-tax-vat`, `admin-promotions`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request quote (Priority: P1)

POST/GET quote với cùng payload booking (service lines, time, address, promo code optional) → trả breakdown **deterministic** với engine pricing.

**Acceptance Scenarios**:

1. **Given** valid selection, **When** quote, **Then** có dòng tiền, thuế (nếu bật), khuyến mãi, tổng.
2. **Given** promo không hợp lệ, **When** quote, **Then** **422** với lý do.

---

### User Story 2 - Create booking (Priority: P1)

Xác nhận tạo booking; lưu **line items** + **price snapshot** tại thời điểm đặt (hoặc reference rule ids); status **pending**.

**Acceptance Scenarios**:

1. **Given** address ngoài Hanoi, **When** create, **Then** **422**.
2. **Given** slot không khả dụng (policy), **Then** **409/422** theo planning.
3. **Given** suspended customer, **Then** **403**.

---

### Edge Cases

- **Giá thay đổi** giữa quote và confirm: **409** hoặc accept stale với cảnh báo — **policy in planning** (default: reject nếu delta > threshold).

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **CUS-CRT-001**: Customer MUST obtain a **price quote** via the dedicated quote endpoint, then submit **`quote_id`** on booking creation (**FR-043** parent spec); no booking without a valid quote reference.
- **CUS-CRT-002**: Customer MUST **create** bookings with **service type(s)**, **schedule**, **address** within **Hanoi** (FR-006).
- **CUS-CRT-003**: System MUST persist **booking** with **pricing snapshot** or resolvable rule references aligned with admin catalog.
- **CUS-CRT-004**: System MUST validate **multi-line** payloads when product supports bundles (see parent + admin pricing).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-CC1**: Quote và booking create **khớp** tổng tiền trong golden tests (sau thuế/khuyến mãi theo rule).
