"""Add reviews moderation table

Revision ID: 9fb3f4b9211a
Revises: f2d6b30ac447
Create Date: 2026-04-17 00:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9fb3f4b9211a"
down_revision = "f2d6b30ac447"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=False),
        sa.Column("helper_id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="visible"),
        sa.Column("flagged_reason_code", sa.String(length=64), nullable=True),
        sa.Column("moderated_by", sa.String(), nullable=True),
        sa.Column("moderated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["helper_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["moderated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_id", "reviews", ["id"], unique=False)
    op.create_index("ix_reviews_booking_id", "reviews", ["booking_id"], unique=False)
    op.create_index("ix_reviews_helper_id", "reviews", ["helper_id"], unique=False)
    op.create_index("ix_reviews_customer_id", "reviews", ["customer_id"], unique=False)
    op.create_index("ix_reviews_status", "reviews", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reviews_status", table_name="reviews")
    op.drop_index("ix_reviews_customer_id", table_name="reviews")
    op.drop_index("ix_reviews_helper_id", table_name="reviews")
    op.drop_index("ix_reviews_booking_id", table_name="reviews")
    op.drop_index("ix_reviews_id", table_name="reviews")
    op.drop_table("reviews")
