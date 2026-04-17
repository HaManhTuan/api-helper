"""Add customer quote and booking line items

Revision ID: d8f0bc2e9aa1
Revises: c1de32f9e001
Create Date: 2026-04-17 02:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "d8f0bc2e9aa1"
down_revision = "c1de32f9e001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("line_items", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )

    op.create_table(
        "customerquotes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("quote_code", sa.String(length=64), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("promotion_code", sa.String(length=64), nullable=True),
        sa.Column("surge_multiplier", sa.String(length=20), nullable=False, server_default="1.0"),
        sa.Column("line_items", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("address_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(), nullable=False),
        sa.Column("subtotal_before_tax", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tax_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("promotion_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("customer_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customerquotes_id", "customerquotes", ["id"], unique=False)
    op.create_index("ix_customerquotes_customer_id", "customerquotes", ["customer_id"], unique=False)
    op.create_index("ix_customerquotes_quote_code", "customerquotes", ["quote_code"], unique=True)
    op.create_index("ix_customerquotes_expires_at", "customerquotes", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_customerquotes_expires_at", table_name="customerquotes")
    op.drop_index("ix_customerquotes_quote_code", table_name="customerquotes")
    op.drop_index("ix_customerquotes_customer_id", table_name="customerquotes")
    op.drop_index("ix_customerquotes_id", table_name="customerquotes")
    op.drop_table("customerquotes")
    op.drop_column("bookings", "line_items")
