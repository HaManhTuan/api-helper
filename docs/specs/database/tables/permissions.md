# Table: permissions

## Overview
- **Purpose:** Fine-grained operation permissions (ex: `payouts:approve`).
- **Module:** admin-staff-and-roles.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Permission ID |
| code | VARCHAR(128) | NO | - | Permission code | Permission code |
| resource | VARCHAR(64) | NO | - | Logical resource (bookings, payouts) | Resource |
| action | VARCHAR(64) | NO | - | Action scope (read/write/approve) | Action |
| description | TEXT | YES | NULL | Notes | Description |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| role_permissions | permission_id | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_permissions | id | PRIMARY | Primary key |
| uq_permissions_code | code | UNIQUE | Permission lookup |
