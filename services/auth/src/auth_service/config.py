from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    users_table_name: str
    access_token_ttl: int
    refresh_token_ttl: int
    jwt_secret_value: str | None
    jwt_secret_arn: str | None

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            users_table_name=os.environ["USERS_TABLE_NAME"],
            access_token_ttl=int(os.environ.get("ACCESS_TOKEN_TTL", "900")),
            refresh_token_ttl=int(os.environ.get("REFRESH_TOKEN_TTL", "43200")),
            jwt_secret_value=os.environ.get("JWT_SECRET_VALUE"),
            jwt_secret_arn=os.environ.get("JWT_SECRET_ARN"),
        )


settings = Settings.from_env()
