# Table: insurance_enrollments

## Overview
- **Purpose:** Helper enrollment status per insurance product with effective dates.
- **Module:** admin-insurance-and-risk.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Enrollment ID |
| helper_id | UUID | NO | - | FK to helper user | Helper |
| product_id | UUID | NO | - | FK to insurance product | Product |
| status | VARCHAR(20) | NO | 'pending' | not_enrolled/pending/active/expired/revoked | Status |
| effective_from | DATE | YES | NULL | Coverage start | Effective from |
| effective_to | DATE | YES | NULL | Coverage end | Effective to |
| notes | TEXT | YES | NULL | Internal notes | Notes |
| updated_by | UUID | YES | NULL | Staff actor | Updated by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| helper_id | users.id | CASCADE |
| product_id | insurance_products.id | RESTRICT |
| updated_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_insurance_enrollments | id | PRIMARY | Primary key |
| ix_insurance_enrollments_helper_status | helper_id, status | BTREE | Eligibility checks |
