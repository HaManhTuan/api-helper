# Table: insurance_products

## Overview
- **Purpose:** Insurance coverage products configured by admin.
- **Module:** admin-insurance-and-risk.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Product ID |
| name | VARCHAR(150) | NO | - | Product name | Product name |
| coverage_summary | TEXT | NO | - | Coverage description | Coverage summary |
| premium_model | VARCHAR(30) | NO | - | per_month/per_job/included | Premium model |
| valid_from | DATE | YES | NULL | Product validity start | Valid from |
| valid_to | DATE | YES | NULL | Product validity end | Valid to |
| active | BOOLEAN | NO | true | Activation state | Active |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| insurance_enrollments | product_id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_insurance_products | id | PRIMARY | Primary key |
| ix_insurance_products_active | active | BTREE | Active product list |
