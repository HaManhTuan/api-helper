# Table: payout_lines

## Overview
- **Purpose:** Per-helper payout amounts reconciled from snapshots and adjustments.
- **Module:** admin-payouts-and-settlement.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Payout line ID |
| payout_batch_id | UUID | NO | - | FK to `payout_batches.id` | Batch |
| helper_id | UUID | NO | - | FK to helper user | Helper |
| booking_id | UUID | NO | - | FK to source booking | Booking |
| gross_amount | NUMERIC(12,2) | NO | - | Earnings before adjustments | Gross amount |
| adjustment_amount | NUMERIC(12,2) | NO | 0 | Net adjustment impact | Adjustment amount |
| net_amount | NUMERIC(12,2) | NO | - | Final payable | Net amount |
| status | VARCHAR(20) | NO | 'pending' | pending/paid/failed | Line status |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| payout_batch_id | payout_batches.id | CASCADE |
| helper_id | users.id | RESTRICT |
| booking_id | bookings.id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_payout_lines | id | PRIMARY | Primary key |
| ix_payout_lines_batch_helper | payout_batch_id, helper_id | BTREE | Payroll operations |
