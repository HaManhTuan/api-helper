"""Add privacy request workflow tables

Revision ID: e81f6a2d9c41
Revises: d12ac8ef4b90
Create Date: 2026-04-17 00:00:04.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e81f6a2d9c41"
down_revision = "d12ac8ef4b90"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "privacyrequests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("request_type", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="submitted"),
        sa.Column("legal_basis", sa.String(length=80), nullable=True),
        sa.Column("requested_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resolution_summary", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("completed_by", sa.String(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("export_job_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["completed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_privacyrequests_id", "privacyrequests", ["id"], unique=False)
    op.create_index("ix_privacyrequests_customer_id", "privacyrequests", ["customer_id"], unique=False)
    op.create_index("ix_privacyrequests_status", "privacyrequests", ["status"], unique=False)

    op.create_table(
        "privacyrequestevents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("privacy_request_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=30), nullable=True),
        sa.Column("to_status", sa.String(length=30), nullable=True),
        sa.Column("actor_user_id", sa.String(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["privacy_request_id"], ["privacyrequests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_privacyrequestevents_id", "privacyrequestevents", ["id"], unique=False)
    op.create_index("ix_privacyrequestevents_privacy_request_id", "privacyrequestevents", ["privacy_request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_privacyrequestevents_privacy_request_id", table_name="privacyrequestevents")
    op.drop_index("ix_privacyrequestevents_id", table_name="privacyrequestevents")
    op.drop_table("privacyrequestevents")

    op.drop_index("ix_privacyrequests_status", table_name="privacyrequests")
    op.drop_index("ix_privacyrequests_customer_id", table_name="privacyrequests")
    op.drop_index("ix_privacyrequests_id", table_name="privacyrequests")
    op.drop_table("privacyrequests")
