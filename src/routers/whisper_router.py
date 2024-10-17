from fastapi import Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.database import get_db
from .base_router import BaseRouter
from src.services import WhisperService
from src.models import User
from src.security import get_current_user


class WhisperRouter(BaseRouter):
    def __init__(self):
        super().__init__(WhisperService())
        self._service: WhisperService
        self._router.add_api_route("/transcribe", self.transcribe, methods=["POST"])

    async def transcribe(
        self,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        return await self._service.transcribe(file=file)
