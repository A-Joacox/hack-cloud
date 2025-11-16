from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=3, max_length=80)
    role: Literal["student", "staff", "authority"]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserResponse(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    status: str
    last_login_at: str | None = None


class LoginResponse(BaseModel):
    user: UserResponse
    tokens: AuthTokens
