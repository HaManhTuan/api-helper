"""Add disputes and dispute adjustments tables

Revision ID: d12ac8ef4b90
Revises: c41d5f3b2d12
Create Date: 2026-04-17 00:00:03.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d12ac8ef4b90"
down_revision = "c41d5f3b2d12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "disputes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=False),
        sa.Column("owner_staff_id", sa.String(), nullable=True),
        sa.Column("dispute_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("insurance_claim_id", sa.String(), nullable=True),
        sa.Column("opened_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_staff_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_disputes_id", "disputes", ["id"], unique=False)
    op.create_index("ix_disputes_booking_id", "disputes", ["booking_id"], unique=False)
    op.create_index("ix_disputes_owner_staff_id", "disputes", ["owner_staff_id"], unique=False)
    op.create_index("ix_disputes_dispute_type", "disputes", ["dispute_type"], unique=False)
    op.create_index("ix_disputes_status", "disputes", ["status"], unique=False)
    op.create_index("ix_disputes_insurance_claim_id", "disputes", ["insurance_claim_id"], unique=False)

    op.create_table(
        "disputeadjustments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("dispute_id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("target_party", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["dispute_id"], ["disputes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_disputeadjustments_id", "disputeadjustments", ["id"], unique=False)
    op.create_index("ix_disputeadjustments_dispute_id", "disputeadjustments", ["dispute_id"], unique=False)
    op.create_index("ix_disputeadjustments_booking_id", "disputeadjustments", ["booking_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_disputeadjustments_booking_id", table_name="disputeadjustments")
    op.drop_index("ix_disputeadjustments_dispute_id", table_name="disputeadjustments")
    op.drop_index("ix_disputeadjustments_id", table_name="disputeadjustments")
    op.drop_table("disputeadjustments")

    op.drop_index("ix_disputes_insurance_claim_id", table_name="disputes")
    op.drop_index("ix_disputes_status", table_name="disputes")
    op.drop_index("ix_disputes_dispute_type", table_name="disputes")
    op.drop_index("ix_disputes_owner_staff_id", table_name="disputes")
    op.drop_index("ix_disputes_booking_id", table_name="disputes")
    op.drop_index("ix_disputes_id", table_name="disputes")
    op.drop_table("disputes")
