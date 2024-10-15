from datetime import datetime
from typing import Protocol
from uuid import UUID

from .gender import GenderType


class UserProtocol(Protocol):
    id: UUID
    first_name: str
    email: str
    gender: GenderType
    hashed_password: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
