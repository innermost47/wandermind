from pydub import AudioSegment
from io import BytesIO
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
import whisper
import torch
from fastapi import UploadFile
from fastapi import FastAPI, APIRouter
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
router = APIRouter()

model = whisper.load_model(
    os.environ.get("WHISPER_MODEL"),
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
)
executor = ThreadPoolExecutor()


async def convert_audio_to_wav(file: UploadFile, file_format: str):
    try:
        file_data = await file.read()
        audio_file = BytesIO(file_data)
        audio_file.seek(0)
        if file_format == "webm":
            audio = (
                AudioSegment.from_file(audio_file).set_frame_rate(16000).set_channels(1)
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
        print(f"An error occurred while trying to convert audio to wav: {e}")
        raise e


def transcribe_audio_sync(wav_file: BytesIO):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
            temp_wav_file.write(wav_file.read())
            temp_wav_file.flush()
            result = model.transcribe(temp_wav_file.name)
        return {"transcription": result["text"]}
    except Exception as e:
        print(f"An error occurred while trying to transcribe audio: {e}")
        raise e


async def transcribe_audio(file: UploadFile, file_format: str):
    async with asyncio.Lock():
        loop = asyncio.get_event_loop()
        wav_file = await convert_audio_to_wav(file, file_format)
        return await loop.run_in_executor(executor, transcribe_audio_sync, wav_file)


@app.post("/main")
async def main(file: UploadFile, file_format: str):
    return await transcribe_audio(file, file_format)


def main():
    uvicorn.run(app, host="127.0.0.1", port=8083)


if __name__ == "__main__":
    main()
