# Feature Specification: Admin — Tax, VAT & Price Display Rules

**Feature Branch**: `001-housemaid-booking-api`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: Admin cấu hình **VAT %** (hoặc chế độ), **giá hiển thị** trước/đã gồm thuế, **mã số thuế** nền tảng (metadata), quy tắc **làm tròn** dòng thuế. **Tách** khỏi commission base (đã nói trong pricing: base trước/sau thuế).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin sets VAT rate and display mode (Priority: P1)

Cấu hình global hoặc theo service: **vat_rate**, **price_display_mode** (`inclusive` | `exclusive`).

**Acceptance Scenarios**:

1. **Given** VAT 10% inclusive, **When** quote, **Then** dòng thuế và tổng khớp test.

---

### User Story 2 - Commission base rule (Priority: P1)

**Fixed in planning**: commission tính trên **amount before VAT** hoặc **after** — **must** be single rule system-wide hoặc per service.

## Requirements *(mandatory)*

### Constitution Alignment

Features MUST remain consistent with `.specify/memory/constitution.md`.

### Functional Requirements

- **ADM-TAX-001**: Admin MUST configure **VAT** parameters và **display** rules.
- **ADM-TAX-002**: Quote và **booking snapshot** MUST include **tax breakdown** fields khi có VAT.
- **ADM-TAX-003**: Commission engine MUST use **documented** tax-inclusive/exclusive base.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-T1**: Golden tests: **100%** khớp kỳ vọng thuế + commission.
