from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from .base_router import BaseRouter
from src.services import GenerationService
from src.schemas import GenerateSchema
from src.models import User
from src.security import get_current_user


class GenerationRouter(BaseRouter):
    def __init__(self):
        super().__init__(GenerationService())
        self._service: GenerationService
        self._router.add_api_route("/generate", self.generate, methods=["POST"])

    async def generate(
        self,
        generate_schema: GenerateSchema,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return await self._service.generate(generate_schema=generate_schema)
