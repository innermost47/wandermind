import whisper
import audiosegment
from io import BytesIO
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = whisper.load_model("small", device=device)


def convert_audio_to_wav(file, file_format):
    if file_format == "webm":
        audio = audiosegment.from_file(file, format="webm").resample(
            sample_rate_Hz=16000, channels=1
        )
    elif file_format == "wav":
        audio = audiosegment.from_file(file, format="wav").resample(
            sample_rate_Hz=16000, channels=1
        )
    else:
        raise ValueError("Format audio non supporté")
    wav_file = BytesIO()
    audio.export(wav_file, format="wav")
    wav_file.seek(0)
    return wav_file


def transcribe_audio(file, file_format):
    wav_file = convert_audio_to_wav(file, file_format)
    result = model.transcribe(wav_file)
    return result["text"]
