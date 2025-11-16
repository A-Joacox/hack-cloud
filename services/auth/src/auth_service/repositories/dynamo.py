from __future__ import annotations

import os
from typing import Optional

import boto3

from ..domain.models import User
from .base import UserRepository


def _table_resource(table_name: str):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


class DynamoUserRepository(UserRepository):
    def __init__(self, table_name: str | None = None):
        self.table_name = table_name or os.environ["USERS_TABLE_NAME"]
        self.table = _table_resource(self.table_name)

    def get_user(self, email: str) -> Optional[User]:
        resp = self.table.get_item(Key={"pk": f"USER#{email.lower()}", "sk": "PROFILE"})
        item = resp.get("Item")
        if not item:
            return None
        return User.from_item(item)

    def put_user(self, user: User) -> None:
        self.table.put_item(Item=user.to_item(), ConditionExpression="attribute_not_exists(pk)")

    def update_last_login(self, email: str, timestamp_iso: str) -> None:
        self.table.update_item(
            Key={"pk": f"USER#{email.lower()}", "sk": "PROFILE"},
            UpdateExpression="SET lastLoginAt = :ts, updatedAt = :ts",
            ExpressionAttributeValues={":ts": timestamp_iso},
        )
