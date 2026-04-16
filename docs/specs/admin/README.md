# Admin — functional specifications (Hanoi House Cleaning Booking API)

**Parent feature**: [`../001-housemaid-booking-api/spec.md`](../001-housemaid-booking-api/spec.md)  
**Feature branch**: `001-housemaid-booking-api`  
**Scope**: **Hệ thống quản trị đầy đủ** (không giới hạn MVP): nhiều nhân viên, phân quyền, vận hành, tài chính nội bộ, tuân thủ, và báo cáo. **Cổng thanh toán trực tuyến** vẫn theo **FR-025** ở spec tổng; mọi **cấu hình giá, hoa hồng, đối soát, export** nằm trong phạm vi admin.

| Spec | Nội dung chính |
|------|----------------|
| [admin-auth-and-access.md](admin-auth-and-access.md) | Đăng nhập staff, JWT, RBAC; MFA khuyến nghị cho role nhạy cảm |
| [admin-staff-and-roles.md](admin-staff-and-roles.md) | **Nhiều** admin, **roles**, **permission matrix**, invite staff |
| [admin-customer-accounts.md](admin-customer-accounts.md) | Khách: list/tìm, chi tiết, suspend; **export/xóa** theo policy |
| [admin-helper-moderation.md](admin-helper-moderation.md) | Duyệt helper, bulk, appeal; suspend/reinstate |
| [admin-helper-documents-kyc.md](admin-helper-documents-kyc.md) | **KYC**: giấy tờ, duyệt, chặn nhận việc khi thiếu |
| [admin-booking-operations.md](admin-booking-operations.md) | Booking toàn hệ, lọc, gán/gán lại, hủy |
| [admin-service-pricing-and-commission.md](admin-service-pricing-and-commission.md) | Catalog, giá/vốn/lãi, commission, **multi-line** booking, vùng/surge |
| [admin-tax-vat-and-display.md](admin-tax-vat-and-display.md) | VAT, hiển thị giá, cơ sở tính commission |
| [admin-promotions-and-vouchers.md](admin-promotions-and-vouchers.md) | Khuyến mãi, mã giảm, stacking |
| [admin-insurance-and-risk.md](admin-insurance-and-risk.md) | Bảo hiểm, enrollment, claim, rule gán việc |
| [admin-disputes-and-adjustments.md](admin-disputes-and-adjustments.md) | Tranh chấp, **điều chỉnh** tài chính nội bộ |
| [admin-payouts-and-settlement.md](admin-payouts-and-settlement.md) | **Kỳ chi** helper, batch, approve, export file, đối soát |
| [admin-analytics.md](admin-analytics.md) | KPI, **doanh thu/phí**, cohort cơ bản, **export** CSV/XLSX |
| [admin-reviews-moderation.md](admin-reviews-moderation.md) | Kiểm duyệt đánh giá, aggregate |
| [admin-content-and-policy.md](admin-content-and-policy.md) | FAQ, điều khoản, policy — version & publish |
| [admin-audit-log.md](admin-audit-log.md) | Audit, SIEM webhook optional |

**Gợi ý phụ thuộc kỹ thuật / triển khai**: `staff & roles` → `auth` → `catalog + tax` → `pricing + commission` → `promotions` → `KYC` + `helper moderation` → `booking ops` → `disputes` → `payouts` → `analytics/export` → `reviews` → `content` → `insurance` (song song khi cần) → `audit` (sự kiện từ đầu).
