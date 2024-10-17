from sqlalchemy import Column, Integer, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone
import hashlib

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    api_key = Column(
        Text,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    api_key_expiration = Column(DateTime(timezone=True), nullable=False)
    is_admin = Column(Boolean, default=False)

    def __init__(self, api_key=None, is_admin=False, expiration_in_days=30):
        self.api_key_expiration = datetime.now(timezone.utc) + timedelta(
            days=expiration_in_days
        )
        self.api_key = api_key
        self.is_admin = is_admin

    @staticmethod
    def hash_api_key(api_key: str):
        return hashlib.sha256(api_key.encode()).hexdigest()

    def __repr__(self):
        return f"<User {self.id} - Admin: {self.is_admin}>"
