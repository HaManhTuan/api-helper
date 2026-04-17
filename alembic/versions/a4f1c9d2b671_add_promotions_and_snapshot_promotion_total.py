"""Add promotions and promotion redemptions

Revision ID: a4f1c9d2b671
Revises: 6a1f0b3c9c10
Create Date: 2026-04-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a4f1c9d2b671"
down_revision = "6a1f0b3c9c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "promotions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("promotion_type", sa.String(length=20), nullable=False),
        sa.Column("service_id", sa.String(), nullable=True),
        sa.Column("discount_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("discount_amount", sa.Integer(), nullable=True),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("per_user_limit", sa.Integer(), nullable=True),
        sa.Column("stack_rule", sa.String(length=30), nullable=False, server_default="surge_then_promotion"),
        sa.Column("effective_from", sa.DateTime(), nullable=False),
        sa.Column("effective_to", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["serviceofferings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promotions_id", "promotions", ["id"], unique=False)
    op.create_index("ix_promotions_code", "promotions", ["code"], unique=True)
    op.create_index("ix_promotions_service_id", "promotions", ["service_id"], unique=False)
    op.create_index("ix_promotions_effective_from", "promotions", ["effective_from"], unique=False)
    op.create_index("ix_promotions_effective_to", "promotions", ["effective_to"], unique=False)
    op.create_index("ix_promotions_active", "promotions", ["active"], unique=False)

    op.create_table(
        "promotionredemptions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("promotion_id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=True),
        sa.Column("quote_id", sa.String(), nullable=True),
        sa.Column("redeemed_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="VND"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="consumed"),
        sa.Column("redeemed_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["promotion_id"], ["promotions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promotionredemptions_id", "promotionredemptions", ["id"], unique=False)
    op.create_index("ix_promotionredemptions_promotion_id", "promotionredemptions", ["promotion_id"], unique=False)
    op.create_index("ix_promotionredemptions_customer_id", "promotionredemptions", ["customer_id"], unique=False)
    op.create_index("ix_promotionredemptions_booking_id", "promotionredemptions", ["booking_id"], unique=False)
    op.create_index("ix_promotionredemptions_quote_id", "promotionredemptions", ["quote_id"], unique=False)

    op.add_column(
        "bookingfinancialsnapshots",
        sa.Column("promotion_total", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("bookingfinancialsnapshots", "promotion_total")

    op.drop_index("ix_promotionredemptions_quote_id", table_name="promotionredemptions")
    op.drop_index("ix_promotionredemptions_booking_id", table_name="promotionredemptions")
    op.drop_index("ix_promotionredemptions_customer_id", table_name="promotionredemptions")
    op.drop_index("ix_promotionredemptions_promotion_id", table_name="promotionredemptions")
    op.drop_index("ix_promotionredemptions_id", table_name="promotionredemptions")
    op.drop_table("promotionredemptions")

    op.drop_index("ix_promotions_active", table_name="promotions")
    op.drop_index("ix_promotions_effective_to", table_name="promotions")
    op.drop_index("ix_promotions_effective_from", table_name="promotions")
    op.drop_index("ix_promotions_service_id", table_name="promotions")
    op.drop_index("ix_promotions_code", table_name="promotions")
    op.drop_index("ix_promotions_id", table_name="promotions")
    op.drop_table("promotions")
