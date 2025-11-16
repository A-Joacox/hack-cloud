from __future__ import annotations

from datetime import datetime, timezone

from .models import User
from .schemas import AuthTokens, LoginRequest, LoginResponse, RegisterRequest, UserResponse
from ..repositories.base import UserRepository
from ..utils import jwt_utils, password_utils


class AuthService:
    def __init__(self, repo: UserRepository, access_ttl: int, refresh_ttl: int):
        self.repo = repo
        self.access_ttl = access_ttl
        self.refresh_ttl = refresh_ttl

    def register(self, payload: RegisterRequest) -> UserResponse:
        email = payload.email.lower()
        if self.repo.get_user(email):
            raise ValueError("USER_ALREADY_EXISTS")

        password_hash = password_utils.hash_password(payload.password)
        user = User(
            email=email,
            full_name=payload.full_name,
            role=payload.role,
            password_hash=password_hash,
        )
        self.repo.put_user(user)
        return UserResponse(
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            last_login_at=user.last_login_at,
        )

    def login(self, payload: LoginRequest) -> LoginResponse:
        email = payload.email.lower()
        user = self.repo.get_user(email)
        if not user:
            raise ValueError("INVALID_CREDENTIALS")

        if user.status != "active":
            raise ValueError("USER_DISABLED")

        if not password_utils.verify_password(payload.password, user.password_hash):
            raise ValueError("INVALID_CREDENTIALS")

        now_ts = datetime.now(timezone.utc).isoformat()
        self.repo.update_last_login(user.email, now_ts)

        access_token = jwt_utils.sign_token(
            subject=user.email,
            role=user.role,
            ttl_seconds=self.access_ttl,
            token_type="access",
        )
        refresh_token = jwt_utils.sign_token(
            subject=user.email,
            role=user.role,
            ttl_seconds=self.refresh_ttl,
            token_type="refresh",
        )

        return LoginResponse(
            user=UserResponse(
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                status=user.status,
                last_login_at=now_ts,
            ),
            tokens=AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.access_ttl,
            ),
        )
