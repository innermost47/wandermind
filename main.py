from fastapi import FastAPI
from src.routers import BaseRouter, GenerationRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List
from config import ORIGINS, APP_HOST, APP_PORT


class TouristApp:
    def __init__(self):
        self.app = FastAPI()
        self.routers: List[BaseRouter] = [
            GenerationRouter(),
        ]
        self._initialize_app()

    def _initialize_app(self):
        for router in self.routers:
            self.app.include_router(router._router)

        origins = ORIGINS if ORIGINS is not None else []
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def get_app(self):
        return self.app


if __name__ == "__main__":
    try:
        tourist_app = TouristApp()
        app = tourist_app.get_app()
        if not APP_HOST or not APP_PORT:
            print(f"Configuration error: APP_HOST={APP_HOST}, APP_PORT={APP_PORT}")
            raise ValueError("APP_HOST or APP_PORT is not defined")
        uvicorn.run(
            app,
            host=APP_HOST,
            port=APP_PORT,
            log_level="info",
        )
    except Exception as e:
        print(f"An error occured while trying to launch app: {e}")
