from pydub import AudioSegment
from io import BytesIO
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import LOCKS, WHISPER_MODEL
import whisper
import torch
from fastapi import UploadFile


class WhisperUtils:
    def __init__(self):
        self.model = whisper.load_model(
            WHISPER_MODEL,
            device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
        )
        self.executor = ThreadPoolExecutor()

    def convert_audio_to_wav(self, file: UploadFile, file_format: str):
        try:
            if isinstance(file, BytesIO):
                audio_file = file
            else:
                audio_file = BytesIO(file.read())
                audio_file.seek(0)

            if file_format == "webm":
                audio = (
                    AudioSegment.from_file(audio_file)
                    .set_frame_rate(16000)
                    .set_channels(1)
                )
            elif file_format == "wav":
                audio = (
                    AudioSegment.from_file(audio_file, format="wav")
                    .set_frame_rate(16000)
                    .set_channels(1)
                )
            else:
                raise ValueError("Format audio non supporté")
            wav_file = BytesIO()
            audio.export(wav_file, format="wav")
            wav_file.seek(0)
            return wav_file

        except Exception as e:
            print(f"An error occured while trying to convert audio to wav: {e}")
            raise e

    def transcribe_audio_sync(self, file: UploadFile, file_format: str):
        try:
            wav_file = self.convert_audio_to_wav(file, file_format)
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_wav_file:
                temp_wav_file.write(wav_file.read())
                temp_wav_file.flush()
                result = self.model.transcribe(temp_wav_file.name)
            return result["text"]
        except Exception as e:
            print(f"An error occured while trying to transcribe audio: {e}")
            raise e

    async def transcribe_audio(self, file: UploadFile, file_format: str):
        async with LOCKS["WHISPER"]:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, self.transcribe_audio_sync, file, file_format
            )
