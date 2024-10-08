from extensions import db
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
import secrets
import hashlib


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(512), nullable=False)
    token = db.Column(
        db.Text, nullable=False, default=lambda: secrets.token_urlsafe(32)
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    token_expiration = db.Column(db.DateTime(timezone=True), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, email, is_admin=False, expiration_in_days=30):
        self.email = email
        self.created_at = datetime.now(timezone.utc)
        self.token_expiration = datetime.now(timezone.utc) + timedelta(
            days=expiration_in_days
        )
        self.is_admin = is_admin

    @staticmethod
    def hash_token(token: str):
        return hashlib.sha256(token.encode()).hexdigest()

    def __repr__(self):
        return f"<User {self.id} - {self.email} - Admin: {self.is_admin}>"
