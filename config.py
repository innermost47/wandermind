import os
from dotenv import load_dotenv
import asyncio


load_dotenv()

LOCKS = {"WHISPER": asyncio.Lock(), "LLAMA": asyncio.Lock(), "GTTS": asyncio.Lock()}
API_KEYS = {
    "OPENAGENDA": os.environ.get("OPENAGENDA_API_KEY"),
    "FOURSQUARE": os.environ.get("FOURSQUARE_API_KEY"),
}
VERIFY = True if os.environ.get("VERIFY") == "True" else False
ORIGINS = ["*"]
APP_HOST = os.environ.get("APP_HOST")
APP_PORT = int(os.environ.get("APP_PORT"))
LLM_MODEL = os.environ.get("LLM_MODEL")
N_CTX_SIZE = int(os.environ.get("N_CTX_SIZE"))
N_GPU_LAYERS = int(os.environ.get("N_GPU_LAYERS"))
WHISPER_MODEL = os.environ.get("WHISPER_MODEL")
