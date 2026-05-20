from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Payload accepted by `POST /auth/register`."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    """Payload accepted by `POST /auth/login`."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserPublicResponse(BaseModel):
    """Subset of `User` columns safe to expose over the API (no password hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime


class AccessTokenResponse(BaseModel):
    """Response body returned by login containing the bearer token."""

    access_token: str
    token_type: str = "bearer"


class JwtTokenPayload(BaseModel):
    """Decoded JWT claims used internally by the auth dependency."""

    sub: str
    exp: int
