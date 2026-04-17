"""Add report export job table

Revision ID: e4f8a09d2b66
Revises: caa7ad28c173
Create Date: 2026-04-17 01:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e4f8a09d2b66"
down_revision = "caa7ad28c173"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reportexportjobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("file_ref", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("requested_by", sa.String(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reportexportjobs_id", "reportexportjobs", ["id"], unique=False)
    op.create_index("ix_reportexportjobs_report_type", "reportexportjobs", ["report_type"], unique=False)
    op.create_index("ix_reportexportjobs_status", "reportexportjobs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_reportexportjobs_status", table_name="reportexportjobs")
    op.drop_index("ix_reportexportjobs_report_type", table_name="reportexportjobs")
    op.drop_index("ix_reportexportjobs_id", table_name="reportexportjobs")
    op.drop_table("reportexportjobs")
