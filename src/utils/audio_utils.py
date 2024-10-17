import base64
from gtts import gTTS
from bs4 import BeautifulSoup
from markdown import markdown
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import LOCKS
from io import BytesIO

executor = ThreadPoolExecutor()


def strip_markdown(text):
    html = markdown(text)
    cleaned = "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))
    cleaned = re.sub(r"[*_~`#>\[\]\\|]", "", cleaned)
    cleaned = re.sub(r"[-+]", "", cleaned)
    return cleaned


def text_to_speech_sync(text):
    if text:
        plain_text = strip_markdown(text)
        tts = gTTS(text=plain_text, lang="fr")
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode("utf-8")
        return audio_base64
    return None


async def text_to_speech_to_memory(text):
    async with LOCKS["GTTS"]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, text_to_speech_sync, text)
