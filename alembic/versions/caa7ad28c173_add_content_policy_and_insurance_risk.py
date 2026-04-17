"""Add content policy and insurance risk tables

Revision ID: caa7ad28c173
Revises: 9fb3f4b9211a
Create Date: 2026-04-17 00:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "caa7ad28c173"
down_revision = "9fb3f4b9211a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("serviceofferings", sa.Column("insurance_required", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("serviceofferings", sa.Column("insurance_enforcement", sa.String(length=20), nullable=False, server_default="hard"))

    op.create_table(
        "contentblocks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("key", sa.String(length=80), nullable=False),
        sa.Column("locale", sa.String(length=10), nullable=False, server_default="vi"),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("content_format", sa.String(length=20), nullable=False, server_default="markdown"),
        sa.Column("version", sa.String(length=40), nullable=False, server_default="v1"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("published_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contentblocks_id", "contentblocks", ["id"], unique=False)
    op.create_index("ix_contentblocks_key", "contentblocks", ["key"], unique=False)
    op.create_index("ix_contentblocks_locale", "contentblocks", ["locale"], unique=False)
    op.create_index("ix_contentblocks_status", "contentblocks", ["status"], unique=False)

    op.create_table(
        "insuranceproducts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("coverage_summary", sa.Text(), nullable=False),
        sa.Column("premium_model", sa.String(length=40), nullable=False),
        sa.Column("eligibility_rule", sa.String(length=80), nullable=False, server_default="approved_helpers_only"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insuranceproducts_id", "insuranceproducts", ["id"], unique=False)
    op.create_index("ix_insuranceproducts_name", "insuranceproducts", ["name"], unique=False)
    op.create_index("ix_insuranceproducts_active", "insuranceproducts", ["active"], unique=False)

    op.create_table(
        "insuranceenrollments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("helper_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="not_enrolled"),
        sa.Column("effective_from", sa.DateTime(), nullable=True),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["helper_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["insuranceproducts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insuranceenrollments_id", "insuranceenrollments", ["id"], unique=False)
    op.create_index("ix_insuranceenrollments_helper_id", "insuranceenrollments", ["helper_id"], unique=False)
    op.create_index("ix_insuranceenrollments_product_id", "insuranceenrollments", ["product_id"], unique=False)
    op.create_index("ix_insuranceenrollments_status", "insuranceenrollments", ["status"], unique=False)

    op.create_table(
        "insuranceclaims",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=False),
        sa.Column("reporter_role", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="opened"),
        sa.Column("resolution_notes", sa.Text(), nullable=True),
        sa.Column("payout_amount", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insuranceclaims_id", "insuranceclaims", ["id"], unique=False)
    op.create_index("ix_insuranceclaims_booking_id", "insuranceclaims", ["booking_id"], unique=False)
    op.create_index("ix_insuranceclaims_status", "insuranceclaims", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_insuranceclaims_status", table_name="insuranceclaims")
    op.drop_index("ix_insuranceclaims_booking_id", table_name="insuranceclaims")
    op.drop_index("ix_insuranceclaims_id", table_name="insuranceclaims")
    op.drop_table("insuranceclaims")

    op.drop_index("ix_insuranceenrollments_status", table_name="insuranceenrollments")
    op.drop_index("ix_insuranceenrollments_product_id", table_name="insuranceenrollments")
    op.drop_index("ix_insuranceenrollments_helper_id", table_name="insuranceenrollments")
    op.drop_index("ix_insuranceenrollments_id", table_name="insuranceenrollments")
    op.drop_table("insuranceenrollments")

    op.drop_index("ix_insuranceproducts_active", table_name="insuranceproducts")
    op.drop_index("ix_insuranceproducts_name", table_name="insuranceproducts")
    op.drop_index("ix_insuranceproducts_id", table_name="insuranceproducts")
    op.drop_table("insuranceproducts")

    op.drop_index("ix_contentblocks_status", table_name="contentblocks")
    op.drop_index("ix_contentblocks_locale", table_name="contentblocks")
    op.drop_index("ix_contentblocks_key", table_name="contentblocks")
    op.drop_index("ix_contentblocks_id", table_name="contentblocks")
    op.drop_table("contentblocks")

    op.drop_column("serviceofferings", "insurance_enforcement")
    op.drop_column("serviceofferings", "insurance_required")
