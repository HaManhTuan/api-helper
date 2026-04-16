# Table: insurance_claims

## Overview
- **Purpose:** Risk claim intake and resolution workflow for incidents.
- **Module:** admin-insurance-and-risk.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Claim ID |
| booking_id | UUID | YES | NULL | FK to related booking | Booking |
| reporter_role | VARCHAR(20) | NO | - | customer/helper/staff/admin | Reporter role |
| status | VARCHAR(20) | NO | 'opened' | opened/under_review/closed | Claim status |
| description | TEXT | NO | - | Incident description | Description |
| resolution_notes | TEXT | YES | NULL | Final resolution summary | Resolution notes |
| amount_optional | NUMERIC(12,2) | YES | NULL | Informational claim amount | Amount |
| created_by | UUID | NO | - | Staff actor | Created by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| closed_at | TIMESTAMPTZ | YES | NULL | Closed timestamp | Closed at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| booking_id | bookings.id | SET NULL |
| created_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_insurance_claims | id | PRIMARY | Primary key |
| ix_insurance_claims_status | status | BTREE | Claims queue |
