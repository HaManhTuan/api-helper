"""Add payout batch and payout line tables

Revision ID: f2d6b30ac447
Revises: e81f6a2d9c41
Create Date: 2026-04-17 00:11:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f2d6b30ac447"
down_revision = "e81f6a2d9c41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payoutbatchs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending_approval"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("total_lines", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("paid_by", sa.String(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payoutbatchs_id", "payoutbatchs", ["id"], unique=False)
    op.create_index("ix_payoutbatchs_period_start", "payoutbatchs", ["period_start"], unique=False)
    op.create_index("ix_payoutbatchs_period_end", "payoutbatchs", ["period_end"], unique=False)
    op.create_index("ix_payoutbatchs_status", "payoutbatchs", ["status"], unique=False)

    op.create_table(
        "payoutlines",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("payout_batch_id", sa.String(), nullable=False),
        sa.Column("helper_id", sa.String(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="VND"),
        sa.Column("base_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("adjustment_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("booking_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("booking_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["helper_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payout_batch_id"], ["payoutbatchs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payoutlines_id", "payoutlines", ["id"], unique=False)
    op.create_index("ix_payoutlines_payout_batch_id", "payoutlines", ["payout_batch_id"], unique=False)
    op.create_index("ix_payoutlines_helper_id", "payoutlines", ["helper_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payoutlines_helper_id", table_name="payoutlines")
    op.drop_index("ix_payoutlines_payout_batch_id", table_name="payoutlines")
    op.drop_index("ix_payoutlines_id", table_name="payoutlines")
    op.drop_table("payoutlines")

    op.drop_index("ix_payoutbatchs_status", table_name="payoutbatchs")
    op.drop_index("ix_payoutbatchs_period_end", table_name="payoutbatchs")
    op.drop_index("ix_payoutbatchs_period_start", table_name="payoutbatchs")
    op.drop_index("ix_payoutbatchs_id", table_name="payoutbatchs")
    op.drop_table("payoutbatchs")
