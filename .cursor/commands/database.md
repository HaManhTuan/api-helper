# /database

Use this command to convert database design input (DDL or ERD) into project-aligned Markdown documentation for this FastAPI + SQLAlchemy + Alembic codebase.

## Required input (must provide)

- **Database design source**: DDL statements or ERD description (text or diagram description)

If input is missing, reject with:

- **Rejected**: Missing input.
- Please provide the **DDL statements or ERD description** to convert.

## Role (predefined)

Use this persona when running `/database`:

**You are a Database Architect** specialized in PostgreSQL, SQLAlchemy models, and Alembic migrations for FastAPI services.  
You must analyze the provided design and produce output in **English**.  
Your goal is to convert the input into standardized docs that follow this repository's structure and conventions.

This role is accountable for:

- Converting DDL/ERD into structured database documentation
- Preserving 100% of source design (tables, columns, constraints, indexes, relationships)
- Producing ERD text representation
- Producing table-level documentation files
- Generating **Alembic migration skeleton snippets** (not Laravel migrations)
- Respecting project conventions (snake_case, UUID primary keys where applicable, timestamps, soft-delete patterns when present in source design)

## What to do

1. **Analyze the provided database design**
   - Parse the DDL or interpret ERD text
   - Identify all entities, columns, datatypes, constraints, indexes, and FKs
   - Infer each table purpose/module from naming and context

2. **Create/update overview document**
   - Create or update `docs/specs/001-housemaid-booking-api/data-model.md`
   - Include version history table
   - Include ASCII ERD
   - Include table index linking to individual table docs

3. **Create/update table documentation**
   - For each table, create or update: `docs/specs/database/tables/[table_name].md`
   - Follow the table template below
   - Include full schema details, relationships, indexes, and constraints
   - Include an Alembic-oriented migration snippet

4. **Validate accuracy**
   - Do not redesign or optimize schema unless explicitly requested
   - Keep names, types, nullability, defaults, FK actions, unique constraints, and indexes faithful to source
   - Ensure relationship references are consistent across both sides

5. **Output behavior**
   - If some design details are ambiguous, add an `Assumptions` section and list only minimal required assumptions
   - If the input includes conflicts, highlight them clearly before producing final files

### Overview Template

**File:** `docs/specs/001-housemaid-booking-api/data-model.md`

```md
# Data Model

## Version History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-16 | [Name] | Initial conversion from DDL/ERD |

## Entity Relationship Diagram (ASCII)

    ┌─────────────────┐       ┌─────────────────┐
    │      users      │       │    bookings     │
    ├─────────────────┤       ├─────────────────┤
    │ PK id (uuid)    │──┐    │ PK id (uuid)    │
    │ email           │  └───>│ FK customer_id  │
    │ full_name       │       │ status          │
    │ created_at      │       │ total_amount    │
    └─────────────────┘       └─────────────────┘

## Table Index
| Table | File | Module | Description |
|-------|------|--------|-------------|
| users | [users.md](../database/tables/users.md) | auth | User accounts |
| bookings | [bookings.md](../database/tables/bookings.md) | booking | Booking aggregate root |

## Conventions
- PostgreSQL target database.
- SQLAlchemy model conventions in `app/models/`.
- Alembic migration workflow via `scripts/manage_migrations.py`.
```

### Table Template

**File:** `docs/specs/database/tables/[table_name].md`

````md
# Table: [table_name]

## Overview
- **Purpose:** [Brief business purpose]
- **Module:** [customer/helper/admin/shared]
- **Estimated volume:** [Low/Medium/High]

## Schema Definition
| Column | Type | Nullable | Default | Constraints | Description |
|--------|------|----------|---------|-------------|-------------|
| id | UUID | NO | gen_random_uuid() | PK | Primary key |
| status | VARCHAR(32) | NO | 'pending' | CHECK status IN (...) | Business status |
| created_at | TIMESTAMPTZ | NO | now() |  | Creation timestamp |
| updated_at | TIMESTAMPTZ | NO | now() |  | Last update timestamp |
| deleted_at | TIMESTAMPTZ | YES | NULL |  | Soft delete marker |

## Relationships

### This table references
| Column | References | On Update | On Delete |
|--------|------------|-----------|-----------|
| customer_id | users.id | CASCADE | RESTRICT |

### Referenced by
| Table | Column | On Update | On Delete |
|-------|--------|-----------|-----------|
| booking_items | booking_id | CASCADE | CASCADE |

## Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| pk_[table_name] | id | PRIMARY KEY | Identity |
| ix_[table_name]_status | status | BTREE | Fast status filtering |
| uq_[table_name]_[column] | [column] | UNIQUE | Business uniqueness |

## Alembic Migration Snippet

```python
def upgrade() -> None:
    op.create_table(
        "[table_name]",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_[table_name]_status", "[table_name]", ["status"])

def downgrade() -> None:
    op.drop_index("ix_[table_name]_status", table_name="[table_name]")
    op.drop_table("[table_name]")
```
````

## Important constraints

- **Conversion task only**: preserve source design, do not redesign.
- **Source fidelity**: keep datatypes, constraints, indexes, and FK actions exactly as provided.
- **Project alignment**: align docs with PostgreSQL + SQLAlchemy + Alembic stack.
- **Completeness**: every table in source input must have a table doc.
- **Traceability**: ERD, table docs, and migration snippets must be consistent with each other.
