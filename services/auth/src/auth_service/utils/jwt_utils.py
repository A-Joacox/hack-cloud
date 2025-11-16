from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any

import boto3
import jwt

from ..config import settings


@lru_cache(maxsize=1)
def _resolve_secret() -> str:
    if settings.jwt_secret_value:
        return settings.jwt_secret_value

    if settings.jwt_secret_arn:
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=settings.jwt_secret_arn)
        secret_value = resp.get("SecretString")
        if secret_value:
            try:
                parsed = json.loads(secret_value)
                return parsed.get("JWT_SIGNING_KEY") or secret_value
            except json.JSONDecodeError:
                return secret_value

    raise RuntimeError("JWT signing secret not configured")


def sign_token(*, subject: str, role: str, ttl_seconds: int, token_type: str) -> str:
    issued_at = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": int(issued_at.timestamp()),
        "exp": int((issued_at + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    secret = _resolve_secret()
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    secret = _resolve_secret()
    return jwt.decode(token, secret, algorithms=["HS256"])
