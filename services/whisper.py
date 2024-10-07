import whisper
from pydub import AudioSegment
from io import BytesIO

model = whisper.load_model("base")


def convert_audio_to_wav(file, file_format):
    if file_format == "webm":
        audio = AudioSegment.from_file(file, format="webm")
    elif file_format == "wav":
        audio = AudioSegment.from_file(file, format="wav")
    else:
        raise ValueError("Format audio non supporté")

    audio = audio.set_channels(1).set_frame_rate(16000)
    wav_file = BytesIO()
    audio.export(wav_file, format="wav")
    wav_file.seek(0)

    return wav_file


def transcribe_audio(file, file_format):
    wav_file = convert_audio_to_wav(file, file_format)
    result = model.transcribe(wav_file)
    return result["text"]
