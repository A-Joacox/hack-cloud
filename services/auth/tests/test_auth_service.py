from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
import sys

import pytest
from freezegun import freeze_time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("USERS_TABLE_NAME", "UsersTableTest")
os.environ.setdefault("JWT_SECRET_VALUE", "test-secret")

from auth_service.domain.auth_service import AuthService
from auth_service.domain.schemas import LoginRequest, RegisterRequest
from auth_service.domain.models import User
from auth_service.repositories.base import UserRepository
from auth_service.utils import jwt_utils


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: dict[str, User] = {}

    def get_user(self, email: str):
        return self.users.get(email)

    def put_user(self, user: User) -> None:
        if user.email in self.users:
            raise ValueError("Already exists")
        self.users[user.email] = user

    def update_last_login(self, email: str, timestamp_iso: str) -> None:
        if email in self.users:
            self.users[email].last_login_at = timestamp_iso


@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_VALUE", "test-secret")
    jwt_utils._resolve_secret.cache_clear()  # type: ignore[attr-defined]
    yield
    jwt_utils._resolve_secret.cache_clear()  # type: ignore[attr-defined]


def test_register_and_login_flow():
    repo = InMemoryUserRepository()
    service = AuthService(repo=repo, access_ttl=900, refresh_ttl=43200)

    register_payload = RegisterRequest(
        email="user@utec.edu.pe",
        password="SecurePass123",
        full_name="Test User",
        role="student",
    )

    response = service.register(register_payload)
    assert response.email == "user@utec.edu.pe"
    assert repo.users["user@utec.edu.pe"].password_hash != "SecurePass123"

    with freeze_time(datetime(2025, 1, 1, tzinfo=timezone.utc)):
        login_payload = LoginRequest(email="user@utec.edu.pe", password="SecurePass123")
        login_resp = service.login(login_payload)
        claims = jwt_utils.verify_token(login_resp.tokens.access_token)

    assert login_resp.user.email == "user@utec.edu.pe"
    assert "." in login_resp.tokens.access_token
    assert claims["sub"] == "user@utec.edu.pe"
    assert claims["role"] == "student"


def test_login_fails_with_wrong_password():
    repo = InMemoryUserRepository()
    service = AuthService(repo=repo, access_ttl=900, refresh_ttl=43200)

    service.register(
        RegisterRequest(
            email="user@utec.edu.pe",
            password="SecurePass123",
            full_name="Test User",
            role="student",
        )
    )

    with pytest.raises(ValueError) as err:
        service.login(LoginRequest(email="user@utec.edu.pe", password="invalid"))

    assert err.value.args[0] == "INVALID_CREDENTIALS"
