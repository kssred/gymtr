from abc import abstractmethod
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import DBAPIError

from src.core.types import ID
from src.core.types.user import UserProtocol
from src.models.user import UserModel
from src.utils.repository import SQLAlchemyRepository
from src.utils.repository.base import RepositoryABC
from src.utils.repository.exceptions import RepositoryException


class IUserRepository(RepositoryABC[UserProtocol, ID]):
    @abstractmethod
    async def clean_not_verified(self, email: str) -> None:
        """
        Удалить email у не подтверждённых пользователей

        :param email: Email адрес
        """
        raise NotImplementedError


class UserRepository(IUserRepository[UUID], SQLAlchemyRepository[UserProtocol, UUID]):
    model = UserModel

    async def clean_not_verified(self, email: str) -> None:
        stmt = update(self.model).filter_by(email=email).values({"email": None})
        try:
            await self.session.execute(stmt)
        except DBAPIError:
            raise RepositoryException("Ошибка при очистке email")
