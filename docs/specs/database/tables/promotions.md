# Table: promotions

## Overview
- **Purpose:** Promotion/voucher campaign configuration for quote and booking pricing.
- **Module:** admin-promotions-and-vouchers.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Promotion ID |
| code | VARCHAR(64) | NO | - | Voucher code | Promotion code |
| promotion_type | VARCHAR(20) | NO | - | percent/fixed/conditional | Promotion type |
| service_id | UUID | YES | NULL | Optional scoped service | Service scope |
| discount_percent | NUMERIC(5,2) | YES | NULL | Percent discount | Discount percent |
| discount_amount | NUMERIC(12,2) | YES | NULL | Fixed discount amount | Discount amount |
| max_redemptions | INTEGER | YES | NULL | Global usage cap | Max redemptions |
| per_user_limit | INTEGER | YES | NULL | Per-user usage cap | Per-user limit |
| stack_rule | VARCHAR(30) | NO | 'deterministic' | Stacking rule with surge/tax | Stacking rule |
| effective_from | TIMESTAMPTZ | NO | - | Start date | Effective from |
| effective_to | TIMESTAMPTZ | YES | NULL | End date | Effective to |
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
| pk_promotions | id | PRIMARY | Primary key |
| uq_promotions_code | code | UNIQUE | Voucher lookup |
