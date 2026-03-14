# app/schemas/auth.py
# ─────────────────────────────────────────────────────────────────
# LEARNING NOTE – Auth schemas
#
# These Pydantic models define the shape of auth request/response bodies.
# They appear automatically in the OpenAPI docs at /docs.
#
# Separation of concerns:
#   RegisterIn  – what the client sends to create an account
#   LoginIn     – what the client sends to get a token
#   TokenOut    – what the server returns on success
#   UserOut     – safe user representation (no password hash)
# ─────────────────────────────────────────────────────────────────

from pydantic import BaseModel, EmailStr, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}
