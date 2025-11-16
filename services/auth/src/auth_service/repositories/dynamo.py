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
        self.table_name = table_name or os.environ.get("USERS_TABLE_NAME") or os.environ.get("USERS_TABLE", "AlertaUTEC-Users")
        self.table = _table_resource(self.table_name)

    def get_user(self, email: str) -> Optional[User]:
        # Buscar por email usando el GSI
        resp = self.table.query(
            IndexName="EmailIndex",
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email": email.lower()}
        )
        items = resp.get("Items", [])
        if not items:
            return None
        return User.from_item(items[0])

    def put_user(self, user: User) -> None:
        item = user.to_item()
        # Asegurarse de que tenga userId como clave primaria
        if "pk" in item:
            item["userId"] = item.pop("pk").replace("USER#", "")
        if "sk" in item:
            item.pop("sk")
        
        self.table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(userId)"
        )

    def update_last_login(self, email: str, timestamp_iso: str) -> None:
        # Primero obtener el userId
        user = self.get_user(email)
        if not user:
            return
        
        self.table.update_item(
            Key={"userId": user.user_id},
            UpdateExpression="SET lastLoginAt = :ts, updatedAt = :ts",
            ExpressionAttributeValues={":ts": timestamp_iso},
        )
