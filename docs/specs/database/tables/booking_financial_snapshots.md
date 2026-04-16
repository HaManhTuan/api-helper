# Table: booking_financial_snapshots

## Overview
- **Purpose:** Immutable financial snapshot persisted at booking completion.
- **Module:** admin-service-pricing-and-commission + analytics + payouts.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Snapshot ID |
| booking_id | UUID | NO | - | FK to `bookings.id` | Booking |
| customer_total | NUMERIC(12,2) | NO | - | Final customer amount | Customer total |
| vat_amount | NUMERIC(12,2) | NO | 0 | Tax component | VAT amount |
| promotion_amount | NUMERIC(12,2) | NO | 0 | Discount component | Promotion amount |
| helper_earnings_component | NUMERIC(12,2) | NO | - | Helper payout basis | Helper earnings |
| platform_fee_component | NUMERIC(12,2) | NO | - | Platform revenue basis | Platform fee |
| commission_rule_id | UUID | YES | NULL | Rule used | Commission rule |
| pricing_rule_id | UUID | YES | NULL | Price entry used | Price rule |
| line_items | JSONB | YES | NULL | Multi-line service breakdown | Line items |
| computed_at | TIMESTAMPTZ | NO | now() | Calculation timestamp | Computed at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| booking_id | bookings.id | CASCADE |
| commission_rule_id | commission_rules.id | SET NULL |
| pricing_rule_id | price_book_entries.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_booking_financial_snapshots | id | PRIMARY | Primary key |
| uq_booking_financial_snapshots_booking_id | booking_id | UNIQUE | One canonical snapshot per booking |
