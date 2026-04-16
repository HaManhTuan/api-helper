# Table: commission_rules

## Overview
- **Purpose:** Defines helper/platform split formulas used for completed booking snapshots.
- **Module:** admin-service-pricing-and-commission.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Rule ID |
| service_id | UUID | YES | NULL | Optional service-specific override | Service |
| helper_percent | NUMERIC(5,2) | NO | 0 | Percentage to helper | Helper percent |
| platform_percent | NUMERIC(5,2) | NO | 0 | Percentage to platform | Platform percent |
| fixed_helper_fee | NUMERIC(12,2) | NO | 0 | Optional fixed helper amount | Fixed helper fee |
| fixed_platform_fee | NUMERIC(12,2) | NO | 0 | Optional fixed platform amount | Fixed platform fee |
| tax_base_mode | VARCHAR(20) | NO | 'before_vat' | before_vat / after_vat | Tax base mode |
| effective_from | TIMESTAMPTZ | NO | - | Rule start | Effective from |
| effective_to | TIMESTAMPTZ | YES | NULL | Rule end | Effective to |
| priority | INTEGER | NO | 100 | Rule precedence | Priority |
| active | BOOLEAN | NO | true | Active flag | Active |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| service_id | service_offerings.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_commission_rules | id | PRIMARY | Primary key |
| ix_commission_rules_resolver | service_id, effective_from, effective_to, priority | BTREE | Commission rule resolver |
