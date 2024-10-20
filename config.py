import os
from dotenv import load_dotenv
import asyncio


load_dotenv()

LOCKS = {
    "LLAMA": asyncio.Semaphore(int(os.environ.get("LLAMA_CPP_THREADS"))),
    "GTTS": asyncio.Lock(),
    "ELEVEN_LABS": asyncio.Semaphore(int(os.environ.get("ELEVEN_LABS_THREADS"))),
}
API_KEYS = {
    "OPENAGENDA": os.environ.get("OPENAGENDA_API_KEY"),
    "FOURSQUARE": os.environ.get("FOURSQUARE_API_KEY"),
}
VERIFY = True if os.environ.get("VERIFY") == "True" else False
ORIGINS = ["*"]
APP_HOST = os.environ.get("APP_HOST")
APP_PORT = int(os.environ.get("APP_PORT"))
WHISPER_MODEL = os.environ.get("WHISPER_MODEL")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
LLAMA_CPP_API_URL = os.environ.get("LLAMA_CPP_API_URL")
WHISPER_API_URL = os.environ.get("WHISPER_API_URL")
USE_ELEVEN_LABS = True if os.environ.get("USE_ELEVEN_LABS") == "True" else False
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
