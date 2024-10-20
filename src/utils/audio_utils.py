import base64
from gtts import gTTS
from bs4 import BeautifulSoup
from markdown import markdown
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import (
    LOCKS,
    USE_ELEVEN_LABS,
    ELEVEN_LABS_API_KEY,
    ELEVEN_LABS_MODEL_ID,
    ELEVEN_LABS_VOICE_ID,
)
from io import BytesIO
import aiohttp

executor = ThreadPoolExecutor()


def strip_markdown(text):
    html = markdown(text)
    cleaned = "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))
    cleaned = re.sub(r"[*_~`#>\[\]\\|]", "", cleaned)
    cleaned = re.sub(r"[-+]", "", cleaned)
    return cleaned


def text_to_speech_sync(text: str):
    try:
        if not text or not text.strip():
            return None
        plain_text = strip_markdown(text)
        tts = gTTS(text=plain_text, lang="fr")
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
        return audio_base64
    except Exception as e:
        print(f"An error occured while trying to convert text to speech: {e}")
        return None


async def text_to_speech_eleven_labs(text):
    CHUNK_SIZE = 1024
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_LABS_VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY,
    }

    data = {
        "text": text,
        "model_id": ELEVEN_LABS_MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200:
                audio_buffer = BytesIO()
                async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                    audio_buffer.write(chunk)
                audio_buffer.seek(0)
                audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
                return audio_base64
            else:
                print(f"Erreur : {response.status}")
                return None


async def text_to_speech_to_memory(text):
    if not USE_ELEVEN_LABS:
        async with LOCKS["GTTS"]:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(executor, text_to_speech_sync, text)
    else:
        async with LOCKS["ELEVEN_LABS"]:
            return await text_to_speech_eleven_labs(text)
