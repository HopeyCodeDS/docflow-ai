"""User entity for authentication."""
from uuid import UUID


class User:
    """User entity."""

    def __init__(
        self,
        id: UUID,
        email: str,
        password_hash: str,
        role: str,
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
