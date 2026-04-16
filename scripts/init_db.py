"""
Database initialization script.

This script runs migrations and adds seed data if needed.
Run this script when setting up the application for the first time.
"""
import importlib
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

if "" in sys.path:
    sys.path.remove("")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

command = importlib.import_module("alembic.command")
Config = importlib.import_module("alembic.config").Config
from app.config.staff_rbac import COMMON_PERMISSIONS, COMMON_ROLES
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tax_rule import TaxRule
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("db_init")


def init_db() -> None:
    """Initialize the database structure and seed data"""
    logger.info("Running database migrations...")

    # Run migrations using alembic - migrations use sync SQLAlchemy
    alembic_cfg = Config(os.path.join(Path(__file__).parent.parent, "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed successfully")

    # For scripts, we can use sync SQLAlchemy with the same connection string
    # Get connection string from settings
    from app.config.settings import settings

    # Create sync engine and session for scripts
    sync_engine = create_engine(
        str(settings.DATABASE_URL),
        echo=settings.DB_ECHO,
    )
    SyncSession = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    # Create a database session
    db = SyncSession()
    try:
        role_by_code = _seed_common_roles_permissions(db)
        _seed_default_tax_rule(db)

        # Check if we have any users
        user_count = db.query(User).count()

        # Add admin user if no users exist
        if user_count == 0:
            logger.info("Creating admin user...")
            admin_user = User(
                email="admin@example.com",
                phone="0900000000",
                role="admin",
                status="active",
                password="adminpassword",  # nosec B106 - Development default
            )
            super_admin_role = role_by_code.get("super_admin")
            if super_admin_role:
                admin_user.staff_role_id = super_admin_role.id
            db.add(admin_user)
            db.commit()
            logger.info(f"Admin user created with identifier: {admin_user.identifier}, ID: {admin_user.id}")

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def _seed_common_roles_permissions(db) -> dict[str, Role]:
    """Seed system-managed common roles and permissions."""
    permission_by_code: dict[str, Permission] = {}
    for code in COMMON_PERMISSIONS:
        permission = db.query(Permission).filter(Permission.code == code, Permission.deleted_at.is_(None)).first()
        if not permission:
            parts = code.split(":")
            resource = parts[0]
            action = ":".join(parts[1:]) if len(parts) > 1 else "manage"
            permission = Permission(code=code, resource=resource, action=action, description=code)
            db.add(permission)
            db.flush()
        permission_by_code[code] = permission

    role_by_code: dict[str, Role] = {}
    for role_code, role_config in COMMON_ROLES.items():
        role = db.query(Role).filter(Role.code == role_code, Role.deleted_at.is_(None)).first()
        if not role:
            role = Role(
                name=str(role_config["name"]),
                code=role_code,
                description=str(role_config.get("description", "")),
                is_system="true",
            )
            db.add(role)
            db.flush()

        role_by_code[role_code] = role
        expected_codes = set(role_config["permissions"])  # type: ignore[arg-type]
        existing = (
            db.query(RolePermission)
            .filter(RolePermission.role_id == role.id, RolePermission.deleted_at.is_(None))
            .all()
        )
        existing_permission_ids = {rp.permission_id for rp in existing}
        for permission_code in expected_codes:
            permission = permission_by_code[permission_code]
            if permission.id not in existing_permission_ids:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    db.commit()
    logger.info("Seeded common roles/permissions catalog successfully")
    return role_by_code


def _seed_default_tax_rule(db) -> None:
    """
    Seed a global default VAT rule if none exists.

    Default:
    - VAT 10%
    - inclusive display
    - commission base before VAT
    """
    existing = db.query(TaxRule).filter(TaxRule.deleted_at.is_(None)).count()
    if existing > 0:
        return

    from datetime import datetime

    rule = TaxRule(
        service_offering_id=None,
        vat_rate=10,
        price_display_mode="inclusive",
        commission_base="before_vat",
        rounding_mode="half_up",
        effective_from=datetime(2020, 1, 1),
        effective_to=None,
        priority=0,
        active=True,
    )
    db.add(rule)
    db.commit()
    logger.info("Seeded default tax rule (VAT 10% inclusive, commission base before_vat)")


if __name__ == "__main__":
    logger.info("Starting database initialization")
    init_db()
    logger.info("Database initialization script completed")
