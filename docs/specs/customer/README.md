# Customer — functional specifications (Hanoi House Cleaning Booking API)

**Parent feature**: [`../001-housemaid-booking-api/spec.md`](../001-housemaid-booking-api/spec.md)  
**Feature branch**: `001-housemaid-booking-api`  
**Scope**: Hành vi API cho **role Customer** — đăng ký/đăng nhập, hồ sơ & địa chỉ, **báo giá & tạo booking** (Hà Nội, multi-line), **lịch sử & hủy**, **đánh giá**, xem **tổng tiền/thuế/khuyến mãi** trên đơn, đọc **chính sách** công khai, **yêu cầu** quyền dữ liệu. Liên quan admin: [`../admin/README.md`](../admin/README.md).

| Module spec | Nội dung |
|-------------|----------|
| [customer-auth-and-onboarding.md](customer-auth-and-onboarding.md) | Đăng ký Customer, đăng nhập, session; tài khoản **suspended** |
| [customer-profile-and-preferences.md](customer-profile-and-preferences.md) | Hồ sơ, **địa chỉ đã lưu**, liên hệ |
| [customer-booking-creation-and-pricing.md](customer-booking-creation-and-pricing.md) | Chọn dịch vụ/add-on, **quote** (giá, VAT, promo), tạo booking **trong Hà Nội** |
| [customer-booking-management-and-cancellation.md](customer-booking-management-and-cancellation.md) | Lịch sử, chi tiết (trạng thái, helper gán, **breakdown tiền**), **hủy** theo policy |
| [customer-reviews.md](customer-reviews.md) | Gửi **một** review/đơn đã completed; xem review đã gửi |
| [customer-policies-and-content.md](customer-policies-and-content.md) | Đọc nội dung đã publish (điều khoản, hủy, FAQ) |
| [customer-privacy-requests.md](customer-privacy-requests.md) | Yêu cầu **export/xóa** dữ liệu cá nhân (workflow với admin) |

**Thứ tự gợi ý**: auth → profile → booking create → booking manage → reviews → policies → privacy.
