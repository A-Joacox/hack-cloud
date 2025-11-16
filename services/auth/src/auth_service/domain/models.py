from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Role = Literal["student", "staff", "authority"]


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class User:
    email: str
    full_name: str
    role: Role
    password_hash: str
    user_id: str | None = None
    status: Literal["active", "disabled"] = "active"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    last_login_at: str | None = None

    def to_item(self) -> dict[str, str]:
        from ulid import ULID
        if not self.user_id:
            self.user_id = f"usr_{str(ULID())}"
        
        return {
            "userId": self.user_id,
            "email": self.email.lower(),
            "fullName": self.full_name,
            "role": self.role,
            "passwordHash": self.password_hash,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "lastLoginAt": self.last_login_at,
        }

    @staticmethod
    def from_item(item: dict[str, str]) -> "User":
        return User(
            user_id=item.get("userId"),
            email=item["email"],
            full_name=item["fullName"],
            role=item["role"],
            password_hash=item["passwordHash"],
            status=item.get("status", "active"),
            created_at=item.get("createdAt", utc_now_iso()),
            updated_at=item.get("updatedAt", utc_now_iso()),
            last_login_at=item.get("lastLoginAt"),
        )
