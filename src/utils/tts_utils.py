import os
from uuid import uuid4
from gtts import gTTS
from bs4 import BeautifulSoup
from markdown import markdown
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from config import LOCKS

executor = ThreadPoolExecutor()


def strip_markdown(text):
    html = markdown(text)
    cleaned = "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))
    cleaned = re.sub(r"[*_~`#>\[\]\\|]", "", cleaned)
    cleaned = re.sub(r"[-+]", "", cleaned)
    return cleaned


def text_to_speech_sync(text, file_path):
    plain_text = strip_markdown(text)
    tts = gTTS(text=plain_text, lang="fr")
    with open(file_path, "wb") as f:
        tts.write_to_fp(f)


async def text_to_speech_to_file(text):
    async with LOCKS["GTTS"]:
        file_name = f"audio_{uuid4()}.mp3"
        file_path = os.path.join("src", "audio", file_name)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, text_to_speech_sync, text, file_path)

        return file_name
