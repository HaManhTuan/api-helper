# Feature Specification: Admin — Promotions, Vouchers & Campaigns

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin cấu hình **mã giảm giá**, **giảm %**, **giảm giá cố định**, **điều kiện** (dịch vụ, ngày, user mới), **giới hạn sử dụng**, **stacking rules** với surge (không stack / có thứ tự).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin creates promotion code (Priority: P1)

Tạo **Promotion**: code, loại giảm, ngày hiệu lực, max **redemptions**, **per user** limit, áp dụng dịch vụ.

**Acceptance Scenarios**:

1. **Given** code giảm 20%, **When** booking quote, **Then** giá sau giảm đúng và **commission** tính trên **base sau promotion** (hoặc trước — **fixed in planning**).

---

### User Story 2 - Admin monitors campaign performance (Priority: P2)

Báo cáo: số lần dùng, GMV có mã, chi phí khuyến mãi ước tính.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-PRM-001**: Admin MUST CRUD **promotions** và **voucher codes**.
- **ADM-PRM-002**: Pricing engine MUST apply **promotion** trong **quote** và **final booking** snapshot.
- **ADM-PRM-003**: Stacking với **zone/peak** MUST be documented và **deterministic**.
- **ADM-PRM-004**: Promotion changes MUST audit-log.

### Key Entities

- **Promotion**, **PromotionRedemption** (optional detail).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-M1**: **100%** test matrix: promotion + surge + commission cho **một** kết quả duy nhất.
