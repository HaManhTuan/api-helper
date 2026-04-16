# Table: promotion_redemptions

## Overview
- **Purpose:** Tracks actual promotion usage for quota checks and campaign analytics.
- **Module:** admin-promotions-and-vouchers + analytics.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Redemption ID |
| promotion_id | UUID | NO | - | FK to `promotions.id` | Promotion |
| customer_id | UUID | NO | - | FK to customer user | Customer |
| booking_id | UUID | YES | NULL | FK when redemption is consumed by booking | Booking |
| quote_id | UUID | YES | NULL | Optional pre-booking trace id | Quote ID |
| redeemed_amount | NUMERIC(12,2) | NO | 0 | Discount amount applied | Redeemed amount |
| currency | CHAR(3) | NO | 'VND' | Currency code | Currency |
| status | VARCHAR(20) | NO | 'reserved' | reserved/consumed/released/expired | Redemption status |
| redeemed_at | TIMESTAMPTZ | NO | now() | Reservation/usage timestamp | Redeemed at |
| consumed_at | TIMESTAMPTZ | YES | NULL | Final consumption timestamp | Consumed at |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| promotion_id | promotions.id | RESTRICT |
| customer_id | users.id | RESTRICT |
| booking_id | bookings.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_promotion_redemptions | id | PRIMARY | Primary key |
| ix_promotion_redemptions_promotion_status | promotion_id, status | BTREE | Campaign monitoring |
| ix_promotion_redemptions_customer_id | customer_id | BTREE | Per-user limit checks |
| uq_promotion_redemptions_booking_id | booking_id | UNIQUE PARTIAL | Prevent double consume per booking |
