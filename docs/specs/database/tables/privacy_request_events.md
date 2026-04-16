# Table: privacy_request_events

## Overview
- **Purpose:** Append-only timeline of state changes/actions on privacy requests.
- **Module:** customer-privacy + admin-customer-accounts + audit/compliance.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Event ID |
| privacy_request_id | UUID | NO | - | FK to `privacy_requests.id` | Privacy request |
| event_type | VARCHAR(40) | NO | - | submitted/reviewed/approved/rejected/completed/etc. | Event type |
| from_status | VARCHAR(30) | YES | NULL | Previous request status | From status |
| to_status | VARCHAR(30) | YES | NULL | New request status | To status |
| actor_user_id | UUID | YES | NULL | Actor performing event | Actor |
| metadata | JSONB | YES | NULL | Structured event details | Metadata |
| created_at | TIMESTAMPTZ | NO | now() | Event timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| privacy_request_id | privacy_requests.id | CASCADE |
| actor_user_id | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_privacy_request_events | id | PRIMARY | Primary key |
| ix_privacy_request_events_request_id_created_at | privacy_request_id, created_at | BTREE | Timeline retrieval |
