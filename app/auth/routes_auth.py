from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.auth import (create_access_token, get_password_hash,
                           get_user_by_username, verify_password)
from app.db.deps import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserLogin

router = APIRouter()


@router.post("/register", response_model=Token)  # Registers user and returns access token
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the database and returns an access token.

    Args:
        user (UserCreate): User's data is passed with the UserCreate schema
        db (Session): SQLAlchemy database session.

    Returns:
        Token: A JWT access token and token type for the user that was created.

    Raises:
        HTTPException 400: If the username is already registered.
        HTTPException 500: If a database error occurs during registration.

    Notes:
        - Password is hashed before being stored.
        - Token is returned only after successful registration.
        - Username must be unique.
        - Rollback writing to database successfully implemented
    """
    if get_user_by_username(db, user.username):  # Raise exception if username already exists
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.model_dump(exclude={"password"}), password=hashed_password)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):  # Logs user in by returning access token
    """
    Verifies a user's credentials and returns an access token if successful.

    Args:
        user (UserLogin): The user's information is passed with the UserLogin Schema.
        db (Session): SQLAlchemy database session.

    Returns:
        Token: A JWT access token and token type for the user that logged in.

    Raises:
        HTTPException 400: If the provided credentials are invalid.

    Notes:
        - Verifies username and password in the database.
        - Token is returned in the header for use in authenticated request.
        - Rollback writing to database successfully implemented

    """
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
