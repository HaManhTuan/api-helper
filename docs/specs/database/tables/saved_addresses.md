# Table: saved_addresses

## Overview
- **Purpose:** Customer saved addresses for quicker booking creation.
- **Module:** customer profile and booking creation.
- **Record Volume:** High.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Address ID |
| customer_id | UUID | NO | - | FK to customer in `users.id` | Customer |
| label | VARCHAR(80) | YES | NULL | Home/Office/etc. | Address label |
| contact_name | VARCHAR(150) | YES | NULL | Recipient/contact name | Contact name |
| contact_phone | VARCHAR(20) | YES | NULL | Contact phone at address | Contact phone |
| line1 | VARCHAR(255) | NO | - | Main address line | Line 1 |
| line2 | VARCHAR(255) | YES | NULL | Additional line | Line 2 |
| ward | VARCHAR(100) | YES | NULL | Ward | Ward |
| district | VARCHAR(100) | NO | - | Hanoi district | District |
| city | VARCHAR(100) | NO | 'Hanoi' | Service city | City |
| latitude | NUMERIC(10,7) | YES | NULL | Geo latitude | Latitude |
| longitude | NUMERIC(10,7) | YES | NULL | Geo longitude | Longitude |
| is_default | BOOLEAN | NO | false | Default address flag | Is default |
| created_at | TIMESTAMPTZ | NO | now() | Created timestamp | Created at |
| updated_at | TIMESTAMPTZ | NO | now() | Updated timestamp | Updated at |
| deleted_at | TIMESTAMPTZ | YES | NULL | Soft-delete marker | Deleted at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| customer_id | users.id | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_saved_addresses | id | PRIMARY | Primary key |
| ix_saved_addresses_customer_id | customer_id | BTREE | List addresses per customer |
| ix_saved_addresses_customer_default | customer_id, is_default | BTREE | Resolve default address |
