from gtts import gTTS
from uuid import uuid4
import os
from bs4 import BeautifulSoup
from markdown import markdown


def strip_markdown(text):
    html = markdown(text)
    cleaned = "".join(BeautifulSoup(html, features="html.parser").findAll(text=True))
    return cleaned.replace("**", "")


def text_to_speech(text, file_path):
    plain_text = strip_markdown(text)
    tts = gTTS(text=plain_text, lang="fr")
    with open(file_path, "wb") as f:
        tts.write_to_fp(f)


def text_to_speech_to_file(text):
    file_name = f"audio_{uuid4()}.mp3"
    file_path = os.path.join("static", "audio", file_name)
    text_to_speech(text, file_path)
    return f"/static/audio/{file_name}"
