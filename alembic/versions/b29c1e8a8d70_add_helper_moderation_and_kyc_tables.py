"""Add helper moderation and KYC tables

Revision ID: b29c1e8a8d70
Revises: a4f1c9d2b671
Create Date: 2026-04-17 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b29c1e8a8d70"
down_revision = "a4f1c9d2b671"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "helperprofiles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "service_area",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("approval_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("suspension_reason_code", sa.String(length=64), nullable=True),
        sa.Column("aggregate_rating", sa.Numeric(3, 2), nullable=False, server_default="0"),
        sa.Column("ratings_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_helperprofiles_id", "helperprofiles", ["id"], unique=False)
    op.create_index("ix_helperprofiles_user_id", "helperprofiles", ["user_id"], unique=True)
    op.create_index("ix_helperprofiles_approval_status", "helperprofiles", ["approval_status"], unique=False)

    op.create_table(
        "helperdocumenttypes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_helperdocumenttypes_id", "helperdocumenttypes", ["id"], unique=False)
    op.create_index("ix_helperdocumenttypes_code", "helperdocumenttypes", ["code"], unique=True)
    op.create_index("ix_helperdocumenttypes_required", "helperdocumenttypes", ["required"], unique=False)
    op.create_index("ix_helperdocumenttypes_active", "helperdocumenttypes", ["active"], unique=False)

    op.create_table(
        "helperdocuments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("helper_id", sa.String(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("storage_ref", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending_review"),
        sa.Column("review_reason_code", sa.String(length=64), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["helper_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_helperdocuments_id", "helperdocuments", ["id"], unique=False)
    op.create_index("ix_helperdocuments_helper_id", "helperdocuments", ["helper_id"], unique=False)
    op.create_index("ix_helperdocuments_document_type", "helperdocuments", ["document_type"], unique=False)
    op.create_index("ix_helperdocuments_status", "helperdocuments", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_helperdocuments_status", table_name="helperdocuments")
    op.drop_index("ix_helperdocuments_document_type", table_name="helperdocuments")
    op.drop_index("ix_helperdocuments_helper_id", table_name="helperdocuments")
    op.drop_index("ix_helperdocuments_id", table_name="helperdocuments")
    op.drop_table("helperdocuments")

    op.drop_index("ix_helperdocumenttypes_active", table_name="helperdocumenttypes")
    op.drop_index("ix_helperdocumenttypes_required", table_name="helperdocumenttypes")
    op.drop_index("ix_helperdocumenttypes_code", table_name="helperdocumenttypes")
    op.drop_index("ix_helperdocumenttypes_id", table_name="helperdocumenttypes")
    op.drop_table("helperdocumenttypes")

    op.drop_index("ix_helperprofiles_approval_status", table_name="helperprofiles")
    op.drop_index("ix_helperprofiles_user_id", table_name="helperprofiles")
    op.drop_index("ix_helperprofiles_id", table_name="helperprofiles")
    op.drop_table("helperprofiles")
