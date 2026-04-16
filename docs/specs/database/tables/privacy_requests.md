# Table: privacy_requests

## Overview
- **Purpose:** DSAR workflow for customer privacy requests (export/delete/anonymize).
- **Module:** customer-privacy + admin-customer-accounts.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Privacy request ID |
| customer_id | UUID | NO | - | Request owner (customer user) | Customer |
| request_type | VARCHAR(20) | NO | - | export/delete/anonymize | Request type |
| status | VARCHAR(30) | NO | 'submitted' | submitted/in_review/approved/rejected/completed/cancelled | Status |
| legal_basis | VARCHAR(80) | YES | NULL | Optional legal/policy basis | Legal basis |
| requested_payload | JSONB | YES | NULL | Optional customer-provided details | Request payload |
| resolution_summary | TEXT | YES | NULL | Admin/staff decision notes | Resolution summary |
| reviewed_by | UUID | YES | NULL | Staff/admin reviewer | Reviewed by |
| reviewed_at | TIMESTAMPTZ | YES | NULL | Review timestamp | Reviewed at |
| completed_by | UUID | YES | NULL | Actor completing workflow | Completed by |
| completed_at | TIMESTAMPTZ | YES | NULL | Completion timestamp | Completed at |
| export_job_id | UUID | YES | NULL | Optional link to report export job | Export job |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| customer_id | users.id | RESTRICT |
| reviewed_by | users.id | SET NULL |
| completed_by | users.id | SET NULL |
| export_job_id | report_export_jobs.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_privacy_requests | id | PRIMARY | Primary key |
| ix_privacy_requests_customer_created_at | customer_id, created_at | BTREE | Customer tracking list |
| ix_privacy_requests_status | status | BTREE | Admin workflow queue |
