"""Add tax rules/config and snapshot tax fields

Revision ID: 6a1f0b3c9c10
Revises: 2c3a1a9b4f21
Create Date: 2026-04-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "6a1f0b3c9c10"
down_revision = "2c3a1a9b4f21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "taxrules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("service_offering_id", sa.String(), nullable=True),
        sa.Column("vat_rate", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("price_display_mode", sa.String(length=20), nullable=False, server_default="inclusive"),
        sa.Column("commission_base", sa.String(length=20), nullable=False, server_default="before_vat"),
        sa.Column("rounding_mode", sa.String(length=20), nullable=False, server_default="half_up"),
        sa.Column("effective_from", sa.DateTime(), nullable=False),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_offering_id"], ["serviceofferings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_taxrules_id", "taxrules", ["id"], unique=False)
    op.create_index("ix_taxrules_service_offering_id", "taxrules", ["service_offering_id"], unique=False)
    op.create_index("ix_taxrules_effective_from", "taxrules", ["effective_from"], unique=False)
    op.create_index("ix_taxrules_effective_to", "taxrules", ["effective_to"], unique=False)
    op.create_index("ix_taxrules_priority", "taxrules", ["priority"], unique=False)
    op.create_index("ix_taxrules_active", "taxrules", ["active"], unique=False)

    op.create_table(
        "taxconfigs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column(
            "value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_taxconfigs_id", "taxconfigs", ["id"], unique=False)
    op.create_index("ix_taxconfigs_key", "taxconfigs", ["key"], unique=True)

    op.add_column("bookingfinancialsnapshots", sa.Column("subtotal_before_tax", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("bookingfinancialsnapshots", sa.Column("tax_total", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("bookingfinancialsnapshots", "tax_total")
    op.drop_column("bookingfinancialsnapshots", "subtotal_before_tax")

    op.drop_index("ix_taxconfigs_key", table_name="taxconfigs")
    op.drop_index("ix_taxconfigs_id", table_name="taxconfigs")
    op.drop_table("taxconfigs")

    op.drop_index("ix_taxrules_active", table_name="taxrules")
    op.drop_index("ix_taxrules_priority", table_name="taxrules")
    op.drop_index("ix_taxrules_effective_to", table_name="taxrules")
    op.drop_index("ix_taxrules_effective_from", table_name="taxrules")
    op.drop_index("ix_taxrules_service_offering_id", table_name="taxrules")
    op.drop_index("ix_taxrules_id", table_name="taxrules")
    op.drop_table("taxrules")

