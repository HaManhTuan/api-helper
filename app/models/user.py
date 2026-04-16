from typing import Optional

from sqlalchemy import Column, DateTime, String
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.base_model import BaseModel


class User(BaseModel):
    """User model for authentication"""

    # User identity and auth information
    role = Column(String(20), nullable=False, default="customer")
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="active")
    last_login_at = Column(DateTime, nullable=True)

    def __init__(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "customer",
        status: str = "active",
        password: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize a new user"""
        # Handle kwargs for flexibility (useful for testing and ORM)
        if kwargs:
            for key, value in kwargs.items():
                # Skip relationship fields as they should be handled separately
                if key in []:  # No relationships currently defined
                    continue
                if hasattr(self, key):
                    setattr(self, key, value)

        if role is not None:
            self.role = role
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        if status is not None:
            self.status = status
        if password is not None:
            self.set_password(password)

    def set_password(self, password: str) -> None:
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password against stored hash"""
        return check_password_hash(self.password_hash, password)  # type: ignore[no-any-return]

    @property
    def identifier(self) -> Optional[str]:
        """Primary login identifier: email first, then phone."""
        return self.email or self.phone

    @property
    def username(self) -> str:
        """
        Compatibility alias for legacy code paths.
        Returns the resolved login identifier.
        """
        return self.identifier or ""

    # Relationships
    # No relationships defined - User model is standalone

    def __repr__(self) -> str:
        """String representation"""
        return f"<User(id={self.id}, identifier={self.identifier})>"
