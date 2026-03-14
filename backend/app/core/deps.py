# app/core/deps.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – FastAPI dependencies
#
# `get_current_user` is a reusable FastAPI dependency.
# Any route that needs the authenticated user adds:
#
#   CurrentUser = Annotated[User, Depends(get_current_user)]
#
# FastAPI calls `get_current_user` automatically, extracts the user
# from the JWT, and injects it into the route function.
# If the token is missing or invalid, it raises 401 before the
# route body runs at all.
#
# LEARNING NOTE – OAuth2PasswordBearer
#   This tells FastAPI that the token comes from the
#   `Authorization: Bearer <token>` header.
#   It also makes the "Authorize" button appear in /docs so you can
#   test protected endpoints interactively.
# ─────────────────────────────────────────────────────────────────

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.db.models import User

# The `tokenUrl` points to the login endpoint.
# It's used by /docs to know where to send credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Validate the JWT and return the corresponding User row.
    Raises HTTP 401 if the token is invalid or the user doesn't exist.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = decode_access_token(token)
    except ValueError:
        raise credentials_exc

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exc

    return user


# Convenience type alias – import this in route modules.
CurrentUser = Annotated[User, Depends(get_current_user)]
