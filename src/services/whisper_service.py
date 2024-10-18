from fastapi import UploadFile
from fastapi import HTTPException
import httpx
from config import WHISPER_API_URL


class WhisperService:
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

            async with httpx.AsyncClient() as client:
                files = {
                    "file": (file.filename, file.file, "multipart/form-data"),
                }
                params = {"file_format": file_format}
                response = await client.post(
                    WHISPER_API_URL, files=files, params=params
                )
                if response.status_code == 200:
                    json_response = response.json()
                    return json_response
                else:
                    raise Exception(f"Failed to transcribe audio: {response.text}")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occured while trying to transcribe audio data: {e}",
            )
