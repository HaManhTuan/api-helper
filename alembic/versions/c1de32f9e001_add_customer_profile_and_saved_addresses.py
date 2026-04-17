"""Add customer profile and saved addresses

Revision ID: c1de32f9e001
Revises: e4f8a09d2b66
Create Date: 2026-04-17 01:25:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c1de32f9e001"
down_revision = "e4f8a09d2b66"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customerprofiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("contact_phone", sa.String(length=20), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customerprofiles_id", "customerprofiles", ["id"], unique=False)
    op.create_index("ix_customerprofiles_user_id", "customerprofiles", ["user_id"], unique=True)

    op.create_table(
        "savedaddresss",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("label", sa.String(length=40), nullable=False),
        sa.Column("line", sa.Text(), nullable=False),
        sa.Column("district", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False, server_default="Hanoi"),
        sa.Column("latitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_savedaddresss_id", "savedaddresss", ["id"], unique=False)
    op.create_index("ix_savedaddresss_customer_id", "savedaddresss", ["customer_id"], unique=False)
    op.create_index("ix_savedaddresss_is_default", "savedaddresss", ["is_default"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_savedaddresss_is_default", table_name="savedaddresss")
    op.drop_index("ix_savedaddresss_customer_id", table_name="savedaddresss")
    op.drop_index("ix_savedaddresss_id", table_name="savedaddresss")
    op.drop_table("savedaddresss")

    op.drop_index("ix_customerprofiles_user_id", table_name="customerprofiles")
    op.drop_index("ix_customerprofiles_id", table_name="customerprofiles")
    op.drop_table("customerprofiles")
