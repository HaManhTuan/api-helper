# Table: disputes

## Overview
- **Purpose:** Tracks dispute cases linked to bookings with owner and workflow state.
- **Module:** admin-disputes-and-adjustments.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Dispute ID |
| booking_id | UUID | NO | - | FK to `bookings.id` | Booking |
| owner_staff_id | UUID | YES | NULL | Staff owner for case | Owner staff |
| dispute_type | VARCHAR(40) | NO | - | quality/damage/payment/etc. | Dispute type |
| status | VARCHAR(30) | NO | 'open' | open/investigating/resolved/closed | Status |
| description | TEXT | YES | NULL | Case details | Description |
| insurance_claim_id | UUID | YES | NULL | Optional risk claim link | Insurance claim |
| opened_at | TIMESTAMPTZ | NO | now() | Open timestamp | Opened at |
| resolved_at | TIMESTAMPTZ | YES | NULL | Resolution timestamp | Resolved at |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| booking_id | bookings.id | CASCADE |
| owner_staff_id | users.id | SET NULL |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| dispute_adjustments | dispute_id | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_disputes | id | PRIMARY | Primary key |
| ix_disputes_status_opened_at | status, opened_at | BTREE | Case queue filtering |
