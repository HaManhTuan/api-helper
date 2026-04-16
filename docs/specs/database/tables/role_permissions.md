# Table: role_permissions

## Overview
- **Purpose:** Many-to-many mapping between roles and permissions.
- **Module:** admin-staff-and-roles.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Mapping ID |
| role_id | UUID | NO | - | FK to `roles.id` | Role |
| permission_id | UUID | NO | - | FK to `permissions.id` | Permission |
| granted_by | UUID | YES | NULL | Internal user who changed mapping | Granted by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| role_id | roles.id | CASCADE |
| permission_id | permissions.id | CASCADE |
| granted_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_role_permissions | id | PRIMARY | Primary key |
| uq_role_permissions_pair | role_id, permission_id | UNIQUE | Prevent duplicate grants |
| ix_role_permissions_role_id | role_id | BTREE | Resolve permissions by role |
