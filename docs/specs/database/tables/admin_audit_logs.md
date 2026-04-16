# Table: admin_audit_logs

## Overview
- **Purpose:** Append-only audit trail for sensitive admin/staff actions (FR-018).
- **Module:** admin-audit-log + all admin modules.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Audit ID |
| admin_user_id | UUID | NO | - | Actor (`staff`/`admin`) | Admin user |
| action | VARCHAR(80) | NO | - | Action code (approve, suspend, assign, etc.) | Action |
| entity_type | VARCHAR(60) | NO | - | Target model type | Entity type |
| entity_id | UUID | YES | NULL | Primary target id | Entity ID |
| related_entity_id | UUID | YES | NULL | Secondary target id if needed | Related entity |
| metadata | JSONB | YES | NULL | Before/after summary, reason codes | Metadata |
| created_at | TIMESTAMPTZ | NO | now() | Event timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| admin_user_id | users.id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_admin_audit_logs | id | PRIMARY | Primary key |
| ix_admin_audit_logs_actor_time | admin_user_id, created_at | BTREE | Actor investigation |
| ix_admin_audit_logs_entity | entity_type, entity_id | BTREE | Target traceability |
