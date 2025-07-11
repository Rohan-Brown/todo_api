import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if expire_str is None:  # Int variable not str. Needed for black.
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES environment variable not set")
ACCESS_TOKEN_EXPIRE_MINUTES = int(expire_str)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(
    plain_password, hashed_password
):  # Verifies passed password is hashed password
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):  # Returns password hashed
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:  # Creates access token
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (  # Expiration set to timezone
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(db: Session, username: str):  # Returns user by username string
    return db.query(User).filter(User.username == username).first()
