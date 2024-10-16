from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.models import User
from typing import List, Optional
from datetime import datetime


class UserRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_user(
        self,
        email: str,
        token: str,
        is_admin: bool = False,
        expiration_in_days: int = 30,
    ) -> User:
        new_user = User(
            email=email,
            expiration_in_days=expiration_in_days,
            is_admin=is_admin,
            token=token,
        )
        self.db_session.add(new_user)
        self.db_session.commit()
        self.db_session.refresh(new_user)
        return new_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            return self.db_session.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            return self.db_session.query(User).filter(User.email == email).one()
        except NoResultFound:
            return None

    def get_all_users(self) -> List[User]:
        return self.db_session.query(User).all()

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user is None:
            return None
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db_session.commit()
        self.db_session.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user is None:
            return False

        self.db_session.delete(user)
        self.db_session.commit()
        return True

    def deactivate_expired_tokens(self) -> List[User]:
        now = datetime.utcnow()
        expired_users = (
            self.db_session.query(User).filter(User.token_expiration < now).all()
        )
        for user in expired_users:
            user.token = None
            self.db_session.commit()
        return expired_users
