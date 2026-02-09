#app/auth/router
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import schemas, service
from app.db.session import get_db

from app.core.security import get_current_user
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.TokenResponse)
def signup(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    return service.create_user(db, user_create)

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate user credentials and return JWT tokens.
    """
    return service.authenticate_user(db, credentials)


@router.post("/refresh", response_model=schemas.AccessTokenResponse)
def refresh_token(payload: schemas.RefreshTokenRequest):
    """
    Issue a new access token using a valid refresh token.
    """
    return service.refresh_access_token(payload.refresh_token)

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }