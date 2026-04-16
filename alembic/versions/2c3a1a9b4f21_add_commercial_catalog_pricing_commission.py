"""Add commercial catalog, pricing, commission, and snapshots

Revision ID: 2c3a1a9b4f21
Revises: 9b7a6f4c2d11
Create Date: 2026-04-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "2c3a1a9b4f21"
down_revision = "9b7a6f4c2d11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "serviceofferings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=False, server_default="hour"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_serviceofferings_id", "serviceofferings", ["id"], unique=False)
    op.create_index("ix_serviceofferings_code", "serviceofferings", ["code"], unique=True)
    op.create_index("ix_serviceofferings_active", "serviceofferings", ["active"], unique=False)

    op.create_table(
        "pricebookentrys",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("service_offering_id", sa.String(), nullable=False),
        sa.Column("variant_code", sa.String(length=50), nullable=True),
        sa.Column("zone_code", sa.String(length=50), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("customer_price", sa.Integer(), nullable=False),
        sa.Column("reference_cost", sa.Integer(), nullable=False, server_default="0"),
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
    op.create_index("ix_pricebookentrys_id", "pricebookentrys", ["id"], unique=False)
    op.create_index("ix_pricebookentrys_service_offering_id", "pricebookentrys", ["service_offering_id"], unique=False)
    op.create_index("ix_pricebookentrys_variant_code", "pricebookentrys", ["variant_code"], unique=False)
    op.create_index("ix_pricebookentrys_zone_code", "pricebookentrys", ["zone_code"], unique=False)
    op.create_index("ix_pricebookentrys_effective_from", "pricebookentrys", ["effective_from"], unique=False)
    op.create_index("ix_pricebookentrys_effective_to", "pricebookentrys", ["effective_to"], unique=False)
    op.create_index("ix_pricebookentrys_priority", "pricebookentrys", ["priority"], unique=False)
    op.create_index("ix_pricebookentrys_active", "pricebookentrys", ["active"], unique=False)

    op.create_table(
        "commissionrules",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("service_offering_id", sa.String(), nullable=True),
        sa.Column("helper_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("platform_percent", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("fixed_platform_fee", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fixed_helper_fee", sa.Integer(), nullable=False, server_default="0"),
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
    op.create_index("ix_commissionrules_id", "commissionrules", ["id"], unique=False)
    op.create_index("ix_commissionrules_service_offering_id", "commissionrules", ["service_offering_id"], unique=False)
    op.create_index("ix_commissionrules_effective_from", "commissionrules", ["effective_from"], unique=False)
    op.create_index("ix_commissionrules_effective_to", "commissionrules", ["effective_to"], unique=False)
    op.create_index("ix_commissionrules_priority", "commissionrules", ["priority"], unique=False)
    op.create_index("ix_commissionrules_active", "commissionrules", ["active"], unique=False)

    op.create_table(
        "bookingfinancialsnapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("customer_total", sa.Integer(), nullable=False),
        sa.Column("helper_total", sa.Integer(), nullable=False),
        sa.Column("platform_total", sa.Integer(), nullable=False),
        sa.Column("applied_price_entry_id", sa.String(), nullable=True),
        sa.Column("applied_commission_rule_id", sa.String(), nullable=True),
        sa.Column(
            "line_items",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["applied_commission_rule_id"], ["commissionrules.id"]),
        sa.ForeignKeyConstraint(["applied_price_entry_id"], ["pricebookentrys.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookingfinancialsnapshots_id", "bookingfinancialsnapshots", ["id"], unique=False)
    op.create_index("ix_bookingfinancialsnapshots_booking_id", "bookingfinancialsnapshots", ["booking_id"], unique=True)
    op.create_index("ix_bookingfinancialsnapshots_computed_at", "bookingfinancialsnapshots", ["computed_at"], unique=False)

    op.create_table(
        "commercialauditlogs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("before", sa.Text(), nullable=True),
        sa.Column("after", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_commercialauditlogs_id", "commercialauditlogs", ["id"], unique=False)
    op.create_index("ix_commercialauditlogs_actor_user_id", "commercialauditlogs", ["actor_user_id"], unique=False)
    op.create_index("ix_commercialauditlogs_entity_type", "commercialauditlogs", ["entity_type"], unique=False)
    op.create_index("ix_commercialauditlogs_entity_id", "commercialauditlogs", ["entity_id"], unique=False)
    op.create_index("ix_commercialauditlogs_action", "commercialauditlogs", ["action"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_commercialauditlogs_action", table_name="commercialauditlogs")
    op.drop_index("ix_commercialauditlogs_entity_id", table_name="commercialauditlogs")
    op.drop_index("ix_commercialauditlogs_entity_type", table_name="commercialauditlogs")
    op.drop_index("ix_commercialauditlogs_actor_user_id", table_name="commercialauditlogs")
    op.drop_index("ix_commercialauditlogs_id", table_name="commercialauditlogs")
    op.drop_table("commercialauditlogs")

    op.drop_index("ix_bookingfinancialsnapshots_computed_at", table_name="bookingfinancialsnapshots")
    op.drop_index("ix_bookingfinancialsnapshots_booking_id", table_name="bookingfinancialsnapshots")
    op.drop_index("ix_bookingfinancialsnapshots_id", table_name="bookingfinancialsnapshots")
    op.drop_table("bookingfinancialsnapshots")

    op.drop_index("ix_commissionrules_active", table_name="commissionrules")
    op.drop_index("ix_commissionrules_priority", table_name="commissionrules")
    op.drop_index("ix_commissionrules_effective_to", table_name="commissionrules")
    op.drop_index("ix_commissionrules_effective_from", table_name="commissionrules")
    op.drop_index("ix_commissionrules_service_offering_id", table_name="commissionrules")
    op.drop_index("ix_commissionrules_id", table_name="commissionrules")
    op.drop_table("commissionrules")

    op.drop_index("ix_pricebookentrys_active", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_priority", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_effective_to", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_effective_from", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_zone_code", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_variant_code", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_service_offering_id", table_name="pricebookentrys")
    op.drop_index("ix_pricebookentrys_id", table_name="pricebookentrys")
    op.drop_table("pricebookentrys")

    op.drop_index("ix_serviceofferings_active", table_name="serviceofferings")
    op.drop_index("ix_serviceofferings_code", table_name="serviceofferings")
    op.drop_index("ix_serviceofferings_id", table_name="serviceofferings")
    op.drop_table("serviceofferings")

