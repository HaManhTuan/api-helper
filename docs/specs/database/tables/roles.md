# Table: roles

## Overview
- **Purpose:** Internal RBAC role definitions for staff operations.
- **Module:** admin-staff-and-roles.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Role ID |
| code | VARCHAR(64) | NO | - | Stable role code (ex: `finance`) | Role code |
| name | VARCHAR(120) | NO | - | Human-readable role name | Role name |
| description | TEXT | YES | NULL | Role description | Description |
| is_system | BOOLEAN | NO | false | Protected built-in role marker | System role |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| role_permissions | role_id | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_roles | id | PRIMARY | Primary key |
| uq_roles_code | code | UNIQUE | Stable role lookup |
