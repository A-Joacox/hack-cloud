from __future__ import annotations

import json
from typing import Any, Callable

from aws_lambda_powertools import Logger

from .config import settings
from .domain.auth_service import AuthService
from .domain.schemas import LoginRequest, RegisterRequest
from .repositories.dynamo import DynamoUserRepository
from .utils import jwt_utils

logger = Logger(service="auth-service")

_repo = DynamoUserRepository(settings.users_table_name)
_service = AuthService(
    repo=_repo,
    access_ttl=settings.access_token_ttl,
    refresh_ttl=settings.refresh_token_ttl,
)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    logger.debug("Incoming event", extra={"event": event})
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    raw_path = event.get("rawPath") or event.get("resource")
    body = event.get("body") or "{}"

    if method == "POST" and raw_path == "/auth/register":
        return _handle_request(body, _service.register, RegisterRequest)
    if method == "POST" and raw_path == "/auth/login":
        return _handle_request(body, _service.login, LoginRequest)

    return _response(404, {"message": "Route not found"})


def authorizer_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    token = event["headers"].get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise Exception("Unauthorized")

    try:
        claims = jwt_utils.verify_token(token)
    except Exception as err:  # pylint: disable=broad-except
        logger.warning("Invalid token", extra={"error": str(err)})
        raise Exception("Unauthorized") from err

    return {
        "isAuthorized": True,
        "context": {
            "sub": claims["sub"],
            "role": claims.get("role", "student"),
            "tokenType": claims.get("type"),
        },
    }


def _handle_request(body: str, handler: Callable[[Any], Any], model_cls):
    try:
        parsed_body = json.loads(body or "{}")
        payload = model_cls(**parsed_body)
        result = handler(payload)
        return _response(200, json.loads(result.model_dump_json()))
    except ValueError as err:
        logger.warning("Validation error", extra={"error": str(err)})
        return _response(400, {"message": str(err)})
    except Exception as err:  # pylint: disable=broad-except
        logger.exception("Unhandled error")
        return _response(500, {"message": "Internal server error"})


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }
