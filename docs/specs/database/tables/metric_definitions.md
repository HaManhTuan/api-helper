# Table: metric_definitions

## Overview
- **Purpose:** Canonical metadata and formulas for analytics metrics.
- **Module:** admin-analytics.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Metric definition ID |
| metric_key | VARCHAR(80) | NO | - | Stable code (ex: `bookings_completed_daily`) | Metric key |
| display_name | VARCHAR(150) | NO | - | Dashboard label | Display name |
| category | VARCHAR(50) | NO | - | demand/supply/revenue/quality/etc. | Category |
| aggregation_granularity | VARCHAR(20) | NO | 'daily' | hourly/daily/weekly/monthly | Granularity |
| formula_expression | TEXT | NO | - | Versioned formula definition | Formula expression |
| source_entities | JSONB | NO | - | Source tables/entities list | Source entities |
| filter_schema | JSONB | YES | NULL | Expected filter payload schema | Filter schema |
| timezone | VARCHAR(50) | NO | 'Asia/Hanoi' | Calculation timezone | Timezone |
| unit | VARCHAR(20) | YES | NULL | count/vnd/percent/minutes | Unit |
| active | BOOLEAN | NO | true | Active metric flag | Active |
| version | INTEGER | NO | 1 | Formula version | Version |
| created_by | UUID | YES | NULL | Staff/admin author | Created by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| created_by | users.id | SET NULL |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| report_snapshots | metric_definition_id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_metric_definitions | id | PRIMARY | Primary key |
| uq_metric_definitions_metric_key_version | metric_key, version | UNIQUE | Versioned metric identity |
| ix_metric_definitions_active_category | active, category | BTREE | Dashboard metric discovery |
