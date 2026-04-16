# Table: service_offerings

## Overview
- **Purpose:** Admin-managed service catalog used by quote and booking flows.
- **Module:** admin-service-pricing-and-commission.
- **Record Volume:** Low.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Service ID |
| code | VARCHAR(64) | NO | - | Stable business code | Service code |
| name | VARCHAR(120) | NO | - | Service display name | Service name |
| description | TEXT | YES | NULL | Detailed description | Description |
| unit | VARCHAR(30) | NO | - | hour/m2/package/etc. | Unit |
| metadata | JSONB | YES | NULL | Tags and custom attributes | Metadata |
| active | BOOLEAN | NO | true | Selectable for new bookings | Active |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |

## Relationships
### Referenced by:
| Table | Column | On Delete |
|-------|--------|-----------|
| price_book_entries | service_id | RESTRICT |
| commission_rules | service_id | SET NULL |
| promotions | service_id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_service_offerings | id | PRIMARY | Primary key |
| uq_service_offerings_code | code | UNIQUE | Business reference |
| ix_service_offerings_active | active | BTREE | Catalog filtering |
