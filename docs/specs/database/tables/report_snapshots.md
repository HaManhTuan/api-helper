# Table: report_snapshots

## Overview
- **Purpose:** Cached aggregate outputs for fast dashboard reads.
- **Module:** admin-analytics.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Snapshot ID |
| metric_definition_id | UUID | NO | - | FK to `metric_definitions.id` | Metric definition |
| snapshot_key | VARCHAR(150) | NO | - | Deterministic key from metric+filters+window | Snapshot key |
| period_start | TIMESTAMPTZ | NO | - | Aggregation period start | Period start |
| period_end | TIMESTAMPTZ | NO | - | Aggregation period end | Period end |
| granularity | VARCHAR(20) | NO | - | hourly/daily/weekly/monthly | Granularity |
| filters_hash | VARCHAR(128) | NO | - | Hash of normalized filters | Filters hash |
| filters_payload | JSONB | NO | - | Original filter payload | Filters payload |
| result_payload | JSONB | NO | - | Aggregated metric output | Result payload |
| record_count | BIGINT | NO | 0 | Number of source records included | Record count |
| computed_at | TIMESTAMPTZ | NO | now() | Snapshot computation time | Computed at |
| expires_at | TIMESTAMPTZ | YES | NULL | Cache expiration time | Expires at |
| created_by_job_id | UUID | YES | NULL | Optional export or worker job id | Created by job |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| metric_definition_id | metric_definitions.id | RESTRICT |
| created_by_job_id | report_export_jobs.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_report_snapshots | id | PRIMARY | Primary key |
| uq_report_snapshots_snapshot_key | snapshot_key | UNIQUE | Prevent duplicate cache rows |
| ix_report_snapshots_lookup | metric_definition_id, period_start, period_end, filters_hash | BTREE | Fast cache lookup |
| ix_report_snapshots_expires_at | expires_at | BTREE | Cache eviction jobs |
