# Table: reviews

## Overview
- **Purpose:** Post-completion customer reviews with moderation controls.
- **Module:** customer-reviews + admin-reviews-moderation.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Review ID |
| booking_id | UUID | NO | - | FK to completed booking | Booking |
| customer_id | UUID | NO | - | Review author | Customer |
| helper_id | UUID | NO | - | Reviewed helper | Helper |
| rating | SMALLINT | NO | - | Rating 1..5 | Rating |
| comment | TEXT | YES | NULL | Optional review content | Comment |
| moderation_status | VARCHAR(20) | NO | 'visible' | visible/hidden/flagged | Moderation status |
| moderation_reason_code | VARCHAR(64) | YES | NULL | Structured moderation reason | Moderation reason |
| moderated_by | UUID | YES | NULL | Internal moderator | Moderated by |
| moderated_at | TIMESTAMPTZ | YES | NULL | Moderation timestamp | Moderated at |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| booking_id | bookings.id | RESTRICT |
| customer_id | users.id | RESTRICT |
| helper_id | users.id | RESTRICT |
| moderated_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_reviews | id | PRIMARY | Primary key |
| uq_reviews_booking_id | booking_id | UNIQUE | One review per booking |
| ix_reviews_helper_status | helper_id, moderation_status | BTREE | Aggregate recalculation |
