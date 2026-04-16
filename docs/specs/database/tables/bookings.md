# Table: bookings

## Overview
- **Purpose:** Core operational booking lifecycle with assignment/reassignment and financial linkage.
- **Module:** customer + helper + admin-booking-operations.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Booking ID |
| customer_id | UUID | NO | - | FK to customer user | Customer |
| helper_id | UUID | YES | NULL | FK to assigned helper | Helper |
| quote_id | UUID | NO | - | Required quote per FR-043 | Quote ID |
| status | VARCHAR(20) | NO | 'pending' | pending/accepted/in-progress/completed/cancelled | Booking status |
| scheduled_start | TIMESTAMPTZ | NO | - | Planned start | Scheduled start |
| scheduled_end | TIMESTAMPTZ | YES | NULL | Planned end | Scheduled end |
| address_snapshot | JSONB | NO | - | Structured address at booking time | Address snapshot |
| reassignment_reason_code | VARCHAR(64) | YES | NULL | Reason when helper is changed | Reassignment reason |
| cancellation_reason_code | VARCHAR(64) | YES | NULL | Reason for cancellation | Cancellation reason |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| customer_id | users.id | RESTRICT |
| helper_id | users.id | SET NULL |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| booking_financial_snapshots | booking_id | CASCADE |
| disputes | booking_id | CASCADE |
| insurance_claims | booking_id | SET NULL |
| reviews | booking_id | RESTRICT |
| payout_lines | booking_id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_bookings | id | PRIMARY | Primary key |
| ix_bookings_status_schedule | status, scheduled_start | BTREE | Admin ops filter |
| ix_bookings_customer_id | customer_id | BTREE | Customer history |
| ix_bookings_helper_id | helper_id | BTREE | Helper workloads |
