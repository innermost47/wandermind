from src.utils import (
    WhisperUtils,
)
from fastapi import UploadFile
from fastapi import HTTPException


class WhisperService:
    def __init__(self):
        self._whisper_utils = WhisperUtils()

    async def transcribe(self, file: UploadFile):
        try:
            if file.filename.endswith(".webm"):
                file_format = "webm"
            elif file.filename.endswith(".wav"):
                file_format = "wav"
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format",
                )
            transcription = await self._whisper_utils.transcribe_audio(
                file, file_format
            )
            return {"transcription": transcription}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occured while trying to transcribe audio data: {e}",
            )
