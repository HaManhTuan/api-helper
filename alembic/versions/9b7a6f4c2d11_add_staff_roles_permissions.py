"""Add staff roles and permissions matrix

Revision ID: 9b7a6f4c2d11
Revises: 43d2f1cb7802
Create Date: 2026-04-16 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9b7a6f4c2d11"
down_revision = "43d2f1cb7802"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.String(length=5), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_id", "roles", ["id"], unique=False)
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)
    op.create_index("ix_roles_code", "roles", ["code"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_permissions_id", "permissions", ["id"], unique=False)
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)
    op.create_index("ix_permissions_resource", "permissions", ["resource"], unique=False)
    op.create_index("ix_permissions_action", "permissions", ["action"], unique=False)

    op.create_table(
        "rolepermissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(), nullable=False),
        sa.Column("permission_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    op.create_index("ix_rolepermissions_id", "rolepermissions", ["id"], unique=False)
    op.create_index("ix_rolepermissions_role_id", "rolepermissions", ["role_id"], unique=False)
    op.create_index("ix_rolepermissions_permission_id", "rolepermissions", ["permission_id"], unique=False)

    op.create_table(
        "staffauditlogs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column("target_user_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_staffauditlogs_id", "staffauditlogs", ["id"], unique=False)
    op.create_index("ix_staffauditlogs_actor_user_id", "staffauditlogs", ["actor_user_id"], unique=False)
    op.create_index("ix_staffauditlogs_target_user_id", "staffauditlogs", ["target_user_id"], unique=False)
    op.create_index("ix_staffauditlogs_action", "staffauditlogs", ["action"], unique=False)

    op.add_column("users", sa.Column("staff_role_id", sa.String(), nullable=True))
    op.create_index("ix_users_staff_role_id", "users", ["staff_role_id"], unique=False)
    op.create_foreign_key("fk_users_staff_role_id_roles", "users", "roles", ["staff_role_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_users_staff_role_id_roles", "users", type_="foreignkey")
    op.drop_index("ix_users_staff_role_id", table_name="users")
    op.drop_column("users", "staff_role_id")

    op.drop_index("ix_staffauditlogs_action", table_name="staffauditlogs")
    op.drop_index("ix_staffauditlogs_target_user_id", table_name="staffauditlogs")
    op.drop_index("ix_staffauditlogs_actor_user_id", table_name="staffauditlogs")
    op.drop_index("ix_staffauditlogs_id", table_name="staffauditlogs")
    op.drop_table("staffauditlogs")

    op.drop_index("ix_rolepermissions_permission_id", table_name="rolepermissions")
    op.drop_index("ix_rolepermissions_role_id", table_name="rolepermissions")
    op.drop_index("ix_rolepermissions_id", table_name="rolepermissions")
    op.drop_table("rolepermissions")

    op.drop_index("ix_permissions_action", table_name="permissions")
    op.drop_index("ix_permissions_resource", table_name="permissions")
    op.drop_index("ix_permissions_code", table_name="permissions")
    op.drop_index("ix_permissions_id", table_name="permissions")
    op.drop_table("permissions")

    op.drop_index("ix_roles_code", table_name="roles")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_id", table_name="roles")
    op.drop_table("roles")

