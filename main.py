from fastapi import FastAPI
from src.routers import BaseRouter, GenerationRouter, WhisperRouter, UserRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List
from config import ORIGINS, APP_HOST, APP_PORT, ADMIN_EMAIL
from src.repositories import UserRepository
from src.utils import AuthUtils, send_email, get_email_for_account_creation
from src.models import User
from typing import List
from src.database import get_db
import asyncio


class TouristApp:
    def __init__(self):
        self.app = FastAPI()
        self.routers: List[BaseRouter] = [
            GenerationRouter(),
            UserRouter(),
            WhisperRouter(),
        ]
        self._db = next(get_db())
        self._initialize_app()
        asyncio.run(self._initialize_first_user())

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

    async def _initialize_first_user(self):
        try:
            user_repository = UserRepository()
            users: List[User] = user_repository.get_all_users(db=self._db)
            if not users:
                auth_utils = AuthUtils()
                api_key = auth_utils.generate_api_key()
                is_admin = True
                expiration_in_days = 365
                subject, email_body = get_email_for_account_creation(
                    api_key=api_key, api_key_expiry_days=expiration_in_days
                )
                user_repository.create_user(
                    api_key=User.hash_api_key(api_key),
                    is_admin=is_admin,
                    expiration_in_days=expiration_in_days,
                    db=self._db,
                )
                await send_email(
                    recipient=ADMIN_EMAIL, subject=subject, content=email_body
                )
        except Exception as e:
            print(f"An error occured while trying to create first user: {e}")

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
