from typing import Optional
from sqlalchemy.orm import Session

from ....domain.entities.user import User
from ..models import UserModel


class UserRepository:
    """Repository for User entity."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
        )
