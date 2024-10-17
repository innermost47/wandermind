from src.utils import (
    AuthUtils,
    send_email,
    get_email_for_account_creation,
)
from src.repositories import UserRepository
from src.schemas import UserSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import User


class UserService:
    def __init__(self):
        self._auth_utils = AuthUtils()
        self._user_repository = UserRepository()

    async def create(self, db: Session, user_schema: UserSchema):
        try:
            api_key = self._auth_utils.generate_api_key()
            subject, email_body = get_email_for_account_creation(api_key=api_key)
            self._user_repository.create_user(api_key=User.hash_api_key(api_key), db=db)
            await send_email(
                recipient=user_schema.email, subject=subject, content=email_body
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occured while trying to create user: {e}",
            )
