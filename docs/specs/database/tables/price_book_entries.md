# Table: price_book_entries

## Overview
- **Purpose:** Effective-dated commercial pricing rules by service/zone/time.
- **Module:** admin-service-pricing-and-commission + admin-tax-vat-and-display.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Price entry ID |
| service_id | UUID | NO | - | FK to `service_offerings.id` | Service |
| zone_code | VARCHAR(50) | YES | NULL | Hanoi zone/district scope | Zone |
| customer_price | NUMERIC(12,2) | NO | - | Listed price | Customer price |
| reference_cost | NUMERIC(12,2) | NO | 0 | Internal cost baseline | Reference cost |
| margin_amount | NUMERIC(12,2) | YES | NULL | Stored or derived margin | Margin |
| currency | CHAR(3) | NO | 'VND' | Currency code | Currency |
| peak_multiplier | NUMERIC(5,2) | NO | 1.0 | Surge multiplier | Peak multiplier |
| vat_rate | NUMERIC(5,2) | NO | 0 | VAT percent for display/tax line | VAT rate |
| effective_from | TIMESTAMPTZ | NO | - | Rule start | Effective from |
| effective_to | TIMESTAMPTZ | YES | NULL | Rule end | Effective to |
| priority | INTEGER | NO | 100 | Conflict resolution priority | Priority |
| active | BOOLEAN | NO | true | Rule activation | Active |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| service_id | service_offerings.id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_price_book_entries | id | PRIMARY | Primary key |
| ix_price_book_entries_lookup | service_id, zone_code, effective_from, effective_to | BTREE | Deterministic price resolver |
