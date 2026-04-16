# Table: user_profiles

## Overview
- **Purpose:** Shared profile information for all account roles (customer/helper/staff/admin).
- **Module:** shared profile domain.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Profile ID |
| user_id | UUID | NO | - | FK to `users.id` (1-1) | User |
| full_name | VARCHAR(150) | YES | NULL | Display/legal name | Full name |
| avatar_url | TEXT | YES | NULL | Avatar image URL | Avatar URL |
| date_of_birth | DATE | YES | NULL | Optional DOB | Date of birth |
| gender | VARCHAR(20) | YES | NULL | Optional profile field | Gender |
| preferred_language | VARCHAR(10) | NO | 'vi' | Locale preference | Preferred language |
| timezone | VARCHAR(50) | NO | 'Asia/Hanoi' | UI/display timezone | Timezone |
| metadata | JSONB | YES | NULL | Role-agnostic profile extras | Metadata |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| user_id | users.id | CASCADE |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| customer_profiles | user_profile_id | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_user_profiles | id | PRIMARY | Primary key |
| uq_user_profiles_user_id | user_id | UNIQUE | One profile per account |
