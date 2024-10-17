from fastapi import Depends, HTTPException, Security
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.models import User
from src.database import get_db
from datetime import datetime, timezone
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
PREFIX = "Bearer"


def get_user_by_api_key(api_key: str, db: Session):
    try:
        hashed_key = User.hash_api_key(api_key=api_key)
        return db.query(User).filter(User.api_key == hashed_key).one()
    except NoResultFound:
        raise HTTPException(status_code=401, detail="Invalid API Key")


async def get_current_user(
    api_key: str = Security(api_key_header), db: Session = Depends(get_db)
):
    if api_key is None:
        raise HTTPException(status_code=400, detail="API Key missing")

    if api_key.startswith(PREFIX + " "):
        key = api_key.split(" ")[1].strip()

    user = get_user_by_api_key(key, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if not user.is_admin:
        if user.api_key_expiration and user.api_key_expiration < datetime.now(
            timezone.utc
        ):
            raise HTTPException(status_code=401, detail="API Key expired")

    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return current_user
