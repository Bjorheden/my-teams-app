# app/core/security.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Authentication primitives
#
# This module owns two concerns:
#
# 1. Password hashing (passlib + bcrypt)
#    We NEVER store plain-text passwords. bcrypt is the industry
#    standard: it's slow by design (making brute-force expensive)
#    and includes a random salt so identical passwords produce
#    different hashes.
#
# 2. JWT (JSON Web Tokens) creation and verification (python-jose)
#    A JWT is a signed JSON payload the server hands to the client
#    after login. The client sends it back in every request.
#    The server verifies the signature – no DB lookup needed.
#
#    Structure of a JWT:  header.payload.signature
#    Payload contains:    {"sub": "user@example.com", "exp": <timestamp>}
#    Signed with:         SECRET_KEY using HS256 algorithm
#
# LEARNING NOTE – why a separate module?
#    Keeping crypto logic here isolates it from business logic.
#    If we switch from HS256 → RS256 (asymmetric keys) later, we
#    only change this file.
# ─────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────

# CryptContext handles algorithm selection and automatic upgrades.
# "bcrypt" is the only scheme here; "deprecated='auto'" means older
# schemes (if added later) are flagged and re-hashed on next login.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of `plain`."""
    return str(pwd_context.hash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if `plain` matches the stored `hashed` value."""
    return bool(pwd_context.verify(plain, hashed))


# ── JWT ───────────────────────────────────────────────────────────


def create_access_token(subject: str) -> str:
    """
    Create a signed JWT.

    `subject` is typically the user's email.
    Expiry is set by `settings.jwt_expire_minutes`.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return str(
        jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    )


def decode_access_token(token: str) -> str:
    """
    Decode and verify a JWT. Returns the subject (email) on success.
    Raises ValueError if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        sub: str | None = payload.get("sub")
        if sub is None:
            raise ValueError("Token missing subject claim.")
        return sub
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc
