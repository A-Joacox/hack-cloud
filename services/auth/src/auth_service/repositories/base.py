from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..domain.models import User


class UserRepository(ABC):
    @abstractmethod
    def get_user(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def put_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_last_login(self, email: str, timestamp_iso: str) -> None:
        raise NotImplementedError
