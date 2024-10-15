from abc import ABC
from logging import getLogger
from typing import Any, AsyncGenerator, Optional, Union
from uuid import UUID

from fastapi import Request
from pydantic import HttpUrl

from src.core.types.user import UserProtocol
from src.schemas.user import (
    UserCreateSchema,
    UserPasswordChangeSchema,
    UserUpdateSchema,
)
from src.services.auth.exceptions import (
    AuthServiceError,
    PasswordMatch,
    PasswordMismatch,
    UserAlreadyExist,
    UserNotExist,
    UserServiceError,
)
from src.services.auth.exceptions import InvalidTokenError as AuthInvalidToken
from src.services.auth.mixins import UserHelperMixin
from src.services.auth.password import PasslibPasswordHelper, PasswordHelperABC
from src.services.parsers import URLParser
from src.services.renderers import TemplateRenderer
from src.services.secrets import CryptoUserTokenGenerator, UserTokenGeneratorABC
from src.services.secrets.exceptions import InvalidToken
from src.services.tasks import TaskServiceABC, celery_task_service
from src.tasks.mailing import send_mail
from src.templates import TemplatePath
from src.utils.repository.exceptions import IntegrityError, RepositoryException
from src.utils.uow import SQLAlchemyUoW, UoWABC

logger = getLogger(__name__)


class UserService(ABC, UserHelperMixin):
    """Сервис по работе с пользователями"""

    uow: UoWABC
    password_helper: PasswordHelperABC
    token_generator: UserTokenGeneratorABC
    task_service: TaskServiceABC

    def __init__(
        self,
        uow: Optional[UoWABC] = None,
        password_helper: Optional[PasswordHelperABC] = None,
        token_generator: Optional[UserTokenGeneratorABC] = None,
        task_service: TaskServiceABC = celery_task_service,
    ):
        self.uow = uow if uow else SQLAlchemyUoW()
        self.password_helper = (
            password_helper if password_helper else PasslibPasswordHelper()
        )
        self.token_generator = (
            token_generator if token_generator else CryptoUserTokenGenerator()
        )
        self.task_service = task_service

    async def create(
        self,
        user_data: UserCreateSchema,
        request: Optional[Request] = None,
    ) -> UserProtocol:
        """
        Создаёт пользователя в БД

        :param user_data: Pydantic схема для создания пользователя
        :param request: Опциональный FastAPI Request
        :raises UserAlreadyExist: пользователь уже зарегистрирован со схожими данными
        :raises UserNotVerified: пользователь не подтвержден
        :raises InvalidPasswordException: невалидный пароль
        :return: Созданный пользователь
        """

        user_dict = user_data.model_dump()
        user_exists = await self.exists(**{"email": user_data.email})
        if user_exists:
            raise UserAlreadyExist(error_fields=["email"])

        password: str = user_dict.pop("password")
        password = password.strip()
        user_dict["hashed_password"] = self.password_helper.hash(password)

        await self.validate_password(password, None)

        async with self.uow:
            try:
                created_user = await self.uow.users.create(user_dict)
            except RepositoryException as e:
                raise AuthServiceError(e.reason) from e

            await self.uow.commit()

        return created_user

    async def update(self, user_id: UUID, user_data: UserUpdateSchema) -> UserProtocol:
        """
        Обновляет данные о пользователе в БД

        :param user_id: Id пользователя
        :param user_data: Pydantic схема для изменения пользователя
        :raises UserAlreadyExist: Пользователь уже существует
        :raises AuthServiceError: Ошибка сервиса по работе с пользователями
        :return: Пользователь
        """

        user_dict = user_data.model_dump(exclude_unset=True)
        user_dict.pop("password", None)

        email = user_dict.get("email", None)
        if email:
            user_exist = await self.exists(email=email, is_verified=True)
            if user_exist:
                raise UserAlreadyExist(error_fields=["email"])

            async with self.uow:
                await self.uow.users.clean_not_verified(email)
                await self.uow.commit()

            user_dict["is_verified"] = False

        async with self.uow:
            try:
                updated_user = await self.uow.users.update(user_id, user_dict)
            except IntegrityError as e:
                raise UserAlreadyExist(error_fields=e.error_fields)
            except RepositoryException as e:
                raise AuthServiceError(e.reason)

            await self.uow.commit()

        return updated_user

    async def authenticate(self, email: str, password: str) -> Optional[UserProtocol]:
        """
        Аутентифицирует пользователя по его email/password, и возвращает его

        :param email: Email адрес пользователя
        :param password: Пароль пользователя
        :return: Пользователь
        """

        try:
            user = await self.get_by_email(email)
        except UserNotExist:
            # Запуск хеширования, чтобы избежать timing-атаки
            self.password_helper.hash(password)
            return None

        verified, updated_password_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not verified:
            return None

        if updated_password_hash is not None:
            async with self.uow:
                await self.uow.users.update(
                    user.id, {"hashed_password": updated_password_hash}
                )

                await self.uow.commit()

        return user

    async def change_password(
        self, user: UserProtocol, password_data: UserPasswordChangeSchema
    ) -> UserProtocol:
        """
        Меняет пароль пользователя

        :param user: Пользователь
        :param password_data: Данные о пароле
        :raises PasswordMismatch: Старый пароль не совпадает
        :raises PasswordMatch: Новый и старый пароль одинаковы
        :return: Обновлённый пользователь
        """

        password_dict = password_data.model_dump()
        old_password = password_dict.pop("old_password")
        new_password = password_dict.pop("new_password")

        if old_password == new_password:
            raise PasswordMatch(error_fields=["new_password"])

        is_matched, _ = self.password_helper.verify_and_update(
            old_password, user.hashed_password
        )
        if not is_matched:
            raise PasswordMismatch(error_fields=["old_password"])

        await self.validate_password(new_password, user)

        new_password_hashed = self.password_helper.hash(new_password)
        async with self.uow:
            updated_user = await self.uow.users.update(
                user.id, {"hashed_password": new_password_hashed}
            )

            await self.uow.commit()

        return updated_user

    async def change_email_request(
        self,
        user: UserProtocol,
        email: str,
        frontend_url: Union[str, HttpUrl],
    ) -> None:
        """
        Отправить запрос на смену email на новую почту

        :param email: Email для отправки
        :param frontend_url: URL, по которому необходимо будет перейти для подтверждения
        :raises UserAlreadyExist: Пользователь уже существует
        :raises MailServiceError: Ошибка отправки сообщения
        """

        user_exist = await self.exists(email=email)
        if user_exist:
            raise UserAlreadyExist(
                "Пользователь с такой почтой уже зарегистрирован",
                error_fields=["email"],
            )

        token = self.token_generator.make_token(user, "CHANGE")
        token_encoded = URLParser.quote_url(token)
        base_url = str(frontend_url)
        base_url = base_url.rstrip("/")
        absolute_url = f"{base_url}?token={token_encoded}&email={email}"

        template_data = {
            "url": absolute_url,
        }
        body = TemplateRenderer.render_template(
            template_data, TemplatePath.EMAIL_EMAIL_CHANGE_TXT
        )

        await self.task_service.create_task(
            send_mail,
            subject="Подтверждение изменения почты",
            body=body,
            recipients=[email],
        )

    async def change_email(self, token: str, email: str) -> UserProtocol:
        """
        Изменить email пользователя

        :param token: Сырой токен для валидации запроса
        :param email: Email адрес на который необходимо заменить
        :raises AuthInvalidToken: Невалидный токен
        :raises UserAlreadyExist: Пользователь уже существует
        """

        token_decoded = URLParser.unquote_url(token)
        try:
            user_id = self.token_generator.check_token(token_decoded)
        except InvalidToken:
            raise AuthInvalidToken("Невалидный токен")

        async with self.uow:
            try:
                updated_user = await self.uow.users.update(
                    UUID(user_id), {"email": email, "is_verified": True}
                )
                await self.uow.commit()
            except IntegrityError as e:
                match e.error_fields[0]:
                    case "email":
                        raise UserAlreadyExist(error_fields=e.error_fields)
                    case _:
                        logger.error("Ошибка при смене email", exc_info=e)
                        raise UserServiceError("Ошибка при смене email")
            except RepositoryException as e:
                logger.error("Ошибка при смене email", exc_info=e)
                raise UserServiceError("Ошибка при смене email")

        return updated_user


async def get_user_service() -> AsyncGenerator[UserService, Any]:
    yield UserService()
