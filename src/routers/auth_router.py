from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from .base_router import BaseRouter
from src.services import AuthService
from src.schemas import AuthSchema


class AuthRouter(BaseRouter):
    def __init__(self):
        super().__init__(AuthService())
        self._service: AuthService
        self._router.add_api_route("/login", self.login, methods=["POST"])
        self._router.add_api_route(
            "/check-api-key", self.check_api_key, methods=["POST"]
        )

    async def login(
        self,
        auth_schema: AuthSchema,
        db: Session = Depends(get_db),
    ):
        return await self._service.login(db=db, auth_schema=auth_schema)

    async def check_api_key(
        self,
        auth_schema: AuthSchema,
        db: Session = Depends(get_db),
    ):
        return await self._service.check_api_key(db=db, auth_schema=auth_schema)
