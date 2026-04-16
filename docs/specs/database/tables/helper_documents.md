# Table: helper_documents

## Overview
- **Purpose:** KYC document metadata and review lifecycle for helpers.
- **Module:** admin-helper-documents-kyc.
- **Record Volume:** Medium.

## Schema Definition
| Column | Type | Nullable | Default | Description | Logic name |
|--------|------|----------|---------|-------------|------------|
| id | UUID | NO | gen_random_uuid() | Primary key | Document ID |
| helper_id | UUID | NO | - | FK to helper user | Helper ID |
| document_type | VARCHAR(50) | NO | - | Configurable doc type (ID card, portrait, etc.) | Document type |
| storage_ref | TEXT | NO | - | Object storage key/path | Storage reference |
| mime_type | VARCHAR(100) | NO | - | Must satisfy FR-044 allowlist | MIME type |
| file_size_bytes | BIGINT | NO | - | Max 10 MiB rule validation | File size |
| status | VARCHAR(30) | NO | 'pending_review' | pending_review/approved/rejected/needs_more_info | Review status |
| review_reason_code | VARCHAR(64) | YES | NULL | Structured reason for decision | Review reason |
| reviewed_by | UUID | YES | NULL | Internal reviewer | Reviewed by |
| reviewed_at | TIMESTAMPTZ | YES | NULL | Review timestamp | Reviewed at |
| created_at | TIMESTAMPTZ | NO | now() | Upload timestamp | Created at |

## Relationships
### This table references:
| Column | References | On Delete |
|--------|------------|-----------|
| helper_id | users.id | CASCADE |
| reviewed_by | users.id | SET NULL |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_helper_documents | id | PRIMARY | Primary key |
| ix_helper_documents_helper_status | helper_id, status | BTREE | Review queue by helper |
| ix_helper_documents_document_type | document_type | BTREE | Compliance filtering |
