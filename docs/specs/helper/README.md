# Helper — functional specifications (Hanoi House Cleaning Booking API)

**Parent feature**: [`../001-housemaid-booking-api/spec.md`](../001-housemaid-booking-api/spec.md)  
**Feature branch**: `001-housemaid-booking-api`  
**Scope**: Hành vi API cho **role Helper** — đăng ký, hồ sơ, lịch rảnh, nhận/từ chối việc, cập nhật trạng thái job, xem thu nhập & đánh giá, nộp KYC. Đối chiếu admin: [`../admin/README.md`](../admin/README.md).

| Module spec | Nội dung |
|-------------|----------|
| [helper-auth-and-onboarding.md](helper-auth-and-onboarding.md) | Đăng ký Helper, đăng nhập, trạng thái **pending approval** / **approved** / **suspended** |
| [helper-profile-and-service-area.md](helper-profile-and-service-area.md) | Hồ sơ hiển thị, kỹ năng/dịch vụ, khu vực phục vụ (Hà Nội), bio |
| [helper-availability-schedule.md](helper-availability-schedule.md) | Lịch rảnh (theo ngày / lặp), bật-tắt slot |
| [helper-booking-offers-and-job-lifecycle.md](helper-booking-offers-and-job-lifecycle.md) | Danh sách offer / job của tôi; accept/reject; **pending→accepted→in-progress→completed**; release/reassign |
| [helper-earnings-and-payouts-visibility.md](helper-earnings-and-payouts-visibility.md) | Xem breakdown thu nhập theo job; lịch sử kỳ chi (read-only) |
| [helper-reviews-and-ratings.md](helper-reviews-and-ratings.md) | Đánh giá nhận được; rating tổng hợp (theo policy hiển thị) |
| [helper-documents-and-kyc-upload.md](helper-documents-and-kyc-upload.md) | Upload giấy tờ; trạng thái duyệt; điều kiện được nhận việc |
| [helper-insurance-enrollment-view.md](helper-insurance-enrollment-view.md) | Xem gói bảo hiểm / phạm vi phủ (read); hành động theo policy |

**Thứ tự phụ thuộc gợi ý**: auth → profile → documents/KYC → availability → booking lifecycle → earnings → reviews → insurance view.
