import whisper
from pydub import AudioSegment
from io import BytesIO
import torch
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = whisper.load_model(os.environ.get("WHISPER_MODEL"), device=device)


def convert_audio_to_wav(file, file_format):
    try:
        if isinstance(file, BytesIO):
            audio_file = file
        else:
            audio_file = BytesIO(file.read())
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
        print(f"An error occured while trying to convert audio to wav: {e}")
        raise e


def transcribe_audio(file, file_format, lock):
    with lock:
        try:
            wav_file = convert_audio_to_wav(file, file_format)
            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as temp_wav_file:
                temp_wav_file.write(wav_file.read())
                temp_wav_file.flush()
                result = model.transcribe(temp_wav_file.name)
            return result["text"]
        except Exception as e:
            print(f"An error occured while trying to transcribe audio: {e}")
            raise e
