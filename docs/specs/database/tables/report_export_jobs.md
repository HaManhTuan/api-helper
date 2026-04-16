# Table: report_export_jobs

## Overview
- **Purpose:** Async export job tracking for analytics/report downloads (CSV/XLSX).
- **Module:** admin-analytics.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Export job ID |
| report_type | VARCHAR(50) | NO | - | bookings/revenue/payouts/cohort/etc. | Report type |
| format | VARCHAR(10) | NO | 'csv' | csv/xlsx | Export format |
| status | VARCHAR(20) | NO | 'queued' | queued/running/succeeded/failed/expired | Job status |
| filters | JSONB | NO | - | Serialized filter payload | Filters |
| requested_by | UUID | NO | - | Staff/admin requester | Requested by |
| file_ref | TEXT | YES | NULL | Storage key/path of generated file | File reference |
| checksum | VARCHAR(128) | YES | NULL | Optional output checksum | Checksum |
| error_code | VARCHAR(64) | YES | NULL | Error code on failure | Error code |
| error_message | TEXT | YES | NULL | Failure details | Error message |
| expires_at | TIMESTAMPTZ | YES | NULL | Download expiry time | Expires at |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| started_at | TIMESTAMPTZ | YES | NULL | Job start time | Started at |
| finished_at | TIMESTAMPTZ | YES | NULL | Job finish time | Finished at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| requested_by | users.id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_report_export_jobs | id | PRIMARY | Primary key |
| ix_report_export_jobs_status_created_at | status, created_at | BTREE | Worker polling/cleanup |
| ix_report_export_jobs_requested_by | requested_by | BTREE | User export history |
