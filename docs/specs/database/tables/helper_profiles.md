# Table: helper_profiles

## Overview
- **Purpose:** Moderation profile and eligibility state for helper accounts.
- **Module:** admin-helper-moderation.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Helper profile ID |
| user_id | UUID | NO | - | FK to helper `users.id` | Helper user |
| display_name | VARCHAR(120) | NO | - | Public profile name | Display name |
| skills | JSONB | YES | NULL | Skill tags list | Skills |
| service_area | JSONB | NO | - | Hanoi districts/service area | Service area |
| approval_status | VARCHAR(20) | NO | 'pending' | pending/approved/suspended/rejected | Approval status |
| suspension_reason_code | VARCHAR(64) | YES | NULL | Structured moderation reason | Suspension reason |
| aggregate_rating | NUMERIC(3,2) | NO | 0 | Cached average rating | Average rating |
| ratings_count | INTEGER | NO | 0 | Count of visible ratings | Ratings count |
| approved_at | TIMESTAMPTZ | YES | NULL | Approval timestamp | Approved at |
| approved_by | UUID | YES | NULL | Internal actor approving | Approved by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| user_id | users.id | CASCADE |
| approved_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_helper_profiles | id | PRIMARY | Primary key |
| uq_helper_profiles_user_id | user_id | UNIQUE | One profile per helper |
| ix_helper_profiles_approval_status | approval_status | BTREE | Moderation queue |
