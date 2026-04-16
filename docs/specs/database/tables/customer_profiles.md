# Table: customer_profiles

## Overview
- **Purpose:** Customer-specific profile and preference fields for booking UX.
- **Module:** customer profile and admin customer accounts.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Customer profile ID |
| user_id | UUID | NO | - | FK to customer in `users.id` | Customer user |
| user_profile_id | UUID | YES | NULL | FK to shared `user_profiles.id` | Shared profile |
| contact_name | VARCHAR(150) | YES | NULL | Booking contact display name | Contact name |
| default_note | TEXT | YES | NULL | Default note for bookings | Default note |
| marketing_opt_in | BOOLEAN | NO | false | Marketing consent flag | Marketing opt-in |
| privacy_consent_version | VARCHAR(32) | YES | NULL | Accepted policy/version marker | Privacy consent version |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| user_id | users.id | CASCADE |
| user_profile_id | user_profiles.id | CASCADE |

### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| saved_addresses | customer_id | CASCADE |
| privacy_requests | customer_id (via users.id) | RESTRICT |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_customer_profiles | id | PRIMARY | Primary key |
| uq_customer_profiles_user_id | user_id | UNIQUE | One profile per customer |
