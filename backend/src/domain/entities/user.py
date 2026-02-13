"""User entity for authentication."""
from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    """User entity."""

    def __init__(
        self,
        id: UUID,
        email: str,
        password_hash: str,
        role: str,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
