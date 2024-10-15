from abc import ABC, abstractmethod
from uuid import UUID

from src.repository.users import IUserRepository


class UoWABC(ABC):
    users: IUserRepository[UUID]

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        exc_type, exc_val, exc_tb = args

        if exc_type is not None:
            await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
