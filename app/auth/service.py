# app/auth/service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.db.models import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


def create_user(db: Session, user_signup):
    """
    Create a new user and return JWT tokens.
    """
    existing_user = db.query(User).filter(User.email == user_signup.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        email=user_signup.email,
        hashed_password=hash_password(user_signup.password),
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    db.refresh(user)

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
        "token_type": "bearer",
    }


def authenticate_user(db: Session, user_login):
    """
    Authenticate user and return JWT tokens.
    """
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not verify_password(
        user_login.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token: str):
    """
    Issue a new access token using a refresh token.
    """
    from jose import jwt, JWTError
    from app.core.config import settings

    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject = payload.get("sub")
        if subject is None:
            raise ValueError
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "access_token": create_access_token(subject),
        "token_type": "bearer",
    }


