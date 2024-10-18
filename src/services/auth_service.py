from src.utils import (
    AuthUtils,
)
from src.repositories import UserRepository
from src.schemas import AuthSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models import User


class AuthService:
    def __init__(self):
        self._auth_utils = AuthUtils()
        self._user_repository = UserRepository()

    async def login(self, db: Session, auth_schema: AuthSchema):
        try:
            user: User = self._user_repository.get_user_by_api_key(
                db=db, api_key=auth_schema.api_key
            )
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"User not found.",
                )
            return user
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occured while trying to login.",
            )

    async def check_api_key(self, db: Session, auth_schema: AuthSchema):
        try:
            user: User = self._user_repository.get_user_by_api_key(
                db=db, api_key=auth_schema.api_key
            )
            if not user:
                return {"success": False}
            return {"success": True}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occured while trying to login.",
            )
