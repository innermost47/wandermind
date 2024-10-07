from gtts import gTTS
from uuid import uuid4
import os


def text_to_speech(text, file_path):
    tts = gTTS(text=text, lang="fr")
    with open(file_path, "wb") as f:
        tts.write_to_fp(f)


def text_to_speech_to_file(text):
    file_name = f"audio_{uuid4()}.mp3"
    file_path = os.path.join("static", "audio", file_name)
    text_to_speech(text, file_path)
    return f"/static/audio/{file_name}"
