from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from .base_router import BaseRouter
from src.services import UserService
from src.schemas import UserSchema
from src.models import User
from src.security import get_current_admin_user


class UserRouter(BaseRouter):
    def __init__(self):
        super().__init__(UserService())
        self._service: UserService
        self._router.add_api_route("/users", self.create, methods=["POST"])

    async def create(
        self,
        user_schema: UserSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user),
    ):
        return await self._service.create(user_schema=user_schema)
