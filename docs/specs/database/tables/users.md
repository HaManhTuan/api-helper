# Table: users

## Overview
- **Purpose:** Unified identity table for customer/helper/staff/admin accounts.
- **Module:** shared (auth + RBAC + account governance).
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | User ID |
| role | VARCHAR(20) | NO | - | `customer` / `helper` / `staff` / `admin` | Role |
| email | VARCHAR(255) | YES | NULL | Login identifier (unique when present) | Email |
| phone | VARCHAR(20) | YES | NULL | Alternative identifier (unique when present) | Phone |
| password_hash | VARCHAR(255) | NO | - | Credential hash only | Password hash |
| status | VARCHAR(20) | NO | 'active' | active/suspended/inactive | Account status |
| last_login_at | TIMESTAMPTZ | YES | NULL | Last successful login | Last login |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |
| deleted_at | TIMESTAMPTZ | YES | NULL | Soft-delete marker | Deleted at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| - | - | - |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| helper_profiles | user_id | CASCADE |
| bookings | customer_id / helper_id | RESTRICT / SET NULL |
| helper_documents | helper_id | CASCADE |
| insurance_enrollments | helper_id | CASCADE |
| reviews | customer_id / helper_id | RESTRICT |
| staff_invites | invited_by / accepted_by | SET NULL |
| admin_audit_logs | admin_user_id | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_users | id | PRIMARY | Primary key |
| uq_users_email | email | UNIQUE PARTIAL | Unique email login |
| uq_users_phone | phone | UNIQUE PARTIAL | Unique phone login |
| ix_users_role_status | role, status | BTREE | Fast admin filters |
