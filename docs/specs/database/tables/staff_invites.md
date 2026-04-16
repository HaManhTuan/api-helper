# Table: staff_invites

## Overview
- **Purpose:** Invite workflow for creating internal staff accounts.
- **Module:** admin-staff-and-roles.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Invite ID |
| email | VARCHAR(255) | NO | - | Target staff email | Invite email |
| role_id | UUID | NO | - | Default role on acceptance | Role |
| token_hash | VARCHAR(255) | NO | - | One-time secure token hash | Token hash |
| status | VARCHAR(20) | NO | 'pending' | pending/accepted/expired/cancelled | Invite status |
| invited_by | UUID | NO | - | Internal actor issuing invite | Invited by |
| accepted_by | UUID | YES | NULL | User account linked when accepted | Accepted by |
| expires_at | TIMESTAMPTZ | NO | - | Expiration cutoff | Expires at |
| accepted_at | TIMESTAMPTZ | YES | NULL | Acceptance timestamp | Accepted at |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| role_id | roles.id | RESTRICT |
| invited_by | users.id | SET NULL |
| accepted_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_staff_invites | id | PRIMARY | Primary key |
| uq_staff_invites_token_hash | token_hash | UNIQUE | One-time token safety |
| ix_staff_invites_email_status | email, status | BTREE | Query pending invites |
