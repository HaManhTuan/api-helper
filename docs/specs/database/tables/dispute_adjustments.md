# Table: dispute_adjustments

## Overview
- **Purpose:** Financial credit/debit records resulting from dispute resolutions.
- **Module:** admin-disputes-and-adjustments.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Adjustment ID |
| dispute_id | UUID | NO | - | FK to `disputes.id` | Dispute |
| booking_id | UUID | NO | - | FK to `bookings.id` for reconciliation | Booking |
| direction | VARCHAR(20) | NO | - | credit/debit | Direction |
| target_party | VARCHAR(20) | NO | - | customer/helper/platform | Target party |
| amount | NUMERIC(12,2) | NO | - | Adjustment amount | Amount |
| reason_code | VARCHAR(64) | NO | - | Structured reason | Reason code |
| note | TEXT | YES | NULL | Optional note | Note |
| created_by | UUID | NO | - | Internal actor | Created by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| dispute_id | disputes.id | CASCADE |
| booking_id | bookings.id | RESTRICT |
| created_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_dispute_adjustments | id | PRIMARY | Primary key |
| ix_dispute_adjustments_booking_id | booking_id | BTREE | Settlement reconciliation |
