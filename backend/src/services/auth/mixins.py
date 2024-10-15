from typing import Union
from uuid import UUID

from src.core.config import settings
from src.core.types.user import UserProtocol
from src.schemas.user import UserCreateSchema
from src.services.auth.exceptions import InvalidPassword, UserNotExist
from src.services.validators.base import ValidatorABC
from src.services.validators.exceptions import PasswordValidationError
from src.utils.loading import import_string
from src.utils.repository.exceptions import RepositoryException
from src.utils.uow import UoWABC


class UserHelperMixin:
    """Класс для валидации данных, связанных с пользователем"""

    uow: UoWABC

    async def get_by_id(self, id_: UUID) -> UserProtocol:
        """
        Получает пользователя по его id

        :param id_: Id пользователя, которого хотим получить
        :raises UserNotExist: Такого пользователя не существует
        :return: Пользователь
        """

        async with self.uow:
            try:
                user = await self.uow.users.get_by_id(id_)
            except RepositoryException:
                raise UserNotExist
        return user

    async def get_by_email(self, email: str) -> UserProtocol:
        """
        Получает пользователя по его email

        :param email: Email адрес пользователя
        :raises UserNotExist: Пользователь не найден
        :return: Пользователь
        """

        async with self.uow:
            try:
                user = await self.uow.users.get(email=email)
            except RepositoryException:
                raise UserNotExist

        return user

    async def exists(self, **filters) -> bool:
        """
        Проверяет есть ли такой пользователь в БД

        :param filters: Фильтры для проверки наличия пользователя в БД
        :return:
        """

        async with self.uow:
            exist = await self.uow.users.exists(**filters)
        return exist

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreateSchema, UserProtocol, None] = None,
    ) -> None:
        """
        Валидация пароля

        :param password: Пароль для валидации
        :param user: Пользователь, у которого данный пароль
        :raises InvalidPasswordException: Пароль не валидный
        :return: `None`, если пароль валидный
        """

        for validator in self.password_validators:
            try:
                validator.validate(password)
            except PasswordValidationError as e:
                raise InvalidPassword(reason=e.reason)

    @property
    def password_validators(self) -> list[ValidatorABC]:
        validators: list[ValidatorABC] = []
        for validator_str in settings.AUTH.PASSWORD_VALIDATORS:
            validator = import_string(validator_str)
            validators.append(validator())

        return validators
