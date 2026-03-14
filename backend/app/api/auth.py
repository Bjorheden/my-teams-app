# app/api/auth.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Auth endpoints
#
# POST /v1/auth/register  – create a new account, return JWT
# POST /v1/auth/login     – verify credentials, return JWT
#
# Why return a token on register?
#   The user just created an account – making them log in immediately
#   after would be a poor UX. Returning the token lets the mobile app
#   go straight to the dashboard.
#
# LEARNING NOTE – HTTP 409 Conflict on duplicate email
#   We check for an existing email before inserting. This gives a clear
#   error message. The `unique=True` DB constraint is a second safety net.
# ─────────────────────────────────────────────────────────────────

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]


# ── POST /auth/register ───────────────────────────────────────────


@router.post(
    "/register",
    response_model=TokenOut,
    status_code=201,
    summary="Register a new account",
    description="Creates a new user account and returns a JWT access token.",
)
def register(body: RegisterIn, db: DbSession) -> TokenOut:
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)


# ── POST /auth/login ──────────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Login",
    description="Verify email + password and return a JWT access token.",
)
def login(body: LoginIn, db: DbSession) -> TokenOut:
    user = db.query(User).filter(User.email == body.email).first()

    # LEARNING NOTE – timing-safe comparison
    # Always call verify_password even if the user doesn't exist.
    # This prevents timing attacks where an attacker can tell the
    # difference between "wrong email" and "wrong password" by measuring
    # how fast the server responds.
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)


# ── GET /auth/me ──────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Returns the authenticated user's profile. Requires a valid JWT.",
)
def get_me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)
