# Table: content_blocks

## Overview
- **Purpose:** Versioned policy/content blocks with draft and published states.
- **Module:** admin-content-and-policy.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Content block ID |
| content_key | VARCHAR(80) | NO | - | terms/privacy/cancellation_policy/etc. | Content key |
| locale | VARCHAR(10) | NO | 'vi' | Language locale | Locale |
| version | INTEGER | NO | 1 | Version number per key+locale | Version |
| body_markdown | TEXT | NO | - | Markdown content body | Content body |
| status | VARCHAR(20) | NO | 'draft' | draft/published/archived | Status |
| published_at | TIMESTAMPTZ | YES | NULL | Publish timestamp | Published at |
| published_by | UUID | YES | NULL | Internal publisher | Published by |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| published_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_content_blocks | id | PRIMARY | Primary key |
| ix_content_blocks_key_locale_status | content_key, locale, status | BTREE | Public policy resolver |
