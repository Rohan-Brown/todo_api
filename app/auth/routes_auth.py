from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.auth import (create_access_token, get_password_hash,
                           get_user_by_username, verify_password)
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserLogin

router = APIRouter()


@router.post("/register", response_model=Token)  # Registers user and returns access token
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):  # Raise exception if username already exists
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.model_dump(exclude={"password"}), password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):  # Logs user in by returning access token
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
