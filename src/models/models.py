from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone
import secrets
import hashlib

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(512), nullable=False, unique=True)
    token = Column(
        Text, nullable=False, default=lambda: User.hash_token(secrets.token_urlsafe(32))
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token_expiration = Column(DateTime(timezone=True), nullable=False)
    is_admin = Column(Boolean, default=False)

    def __init__(self, email, token=None, is_admin=False, expiration_in_days=30):
        self.email = email
        self.token_expiration = datetime.now(timezone.utc) + timedelta(
            days=expiration_in_days
        )
        self.token = token
        self.is_admin = is_admin

    @staticmethod
    def hash_token(token: str):
        return hashlib.sha256(token.encode()).hexdigest()

    def __repr__(self):
        return f"<User {self.id} - {self.email} - Admin: {self.is_admin}>"
