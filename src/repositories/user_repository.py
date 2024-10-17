from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.models import User
from typing import List, Optional
from datetime import datetime, timezone


class UserRepository:

    def create_user(
        self,
        db: Session,
        api_key: str,
        is_admin: bool = False,
        expiration_in_days: int = 30,
    ) -> User:
        try:
            new_user = User(
                expiration_in_days=expiration_in_days,
                is_admin=is_admin,
                api_key=api_key,
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        try:
            return db.query(User).filter(User.id == user_id).one()
        except NoResultFound:
            return None
        finally:
            db.close()

    def get_user_by_api_key(self, db: Session, api_key: str) -> Optional[User]:
        try:
            return (
                db.query(User).filter(User.api_key == User.hash_api_key(api_key)).one()
            )
        except NoResultFound:
            return None
        finally:
            db.close()

    def get_all_users(self, db: Session) -> List[User]:
        try:
            return db.query(User).all()
        except NoResultFound:
            return None
        finally:
            db.close()

    def update_user(self, db: Session, user_id: int, **kwargs) -> Optional[User]:
        try:
            user = self.get_user_by_id(user_id)
            if user is None:
                return None
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def delete_user(self, db: Session, user_id: int) -> bool:
        try:
            user = self.get_user_by_id(user_id)
            if user is None:
                return False

            db.delete(user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def deactivate_expired_tokens(self, db: Session) -> List[User]:
        try:
            now = datetime.now(timezone.utc)
            expired_users = db.query(User).filter(User.api_key_expiration < now).all()
            for user in expired_users:
                user.api_key = None
                db.commit()
            return expired_users
        except NoResultFound:
            return None
        finally:
            db.close()
