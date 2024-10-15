from typing import Any, AsyncGenerator, Optional, Union
from uuid import UUID

from pydantic import HttpUrl

from src.core.types.user import UserProtocol
from src.services.auth.exceptions import InvalidTokenError as AuthInvalidToken
from src.services.auth.exceptions import UserAlreadyVerified
from src.services.auth.mixins import UserHelperMixin
from src.services.auth.password import PasslibPasswordHelper, PasswordHelperABC
from src.services.parsers import URLParser
from src.services.renderers import template_renderer
from src.services.secrets import CryptoUserTokenGenerator, UserTokenGeneratorABC
from src.services.secrets.exceptions import InvalidToken
from src.services.tasks import TaskServiceABC, celery_task_service
from src.tasks import send_mail
from src.templates import TemplatePath
from src.utils.uow import SQLAlchemyUoW, UoWABC


class UserVerificator(UserHelperMixin):
    """Класс для работы с верификацией пользователей и рассылками для неё"""

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

    async def verify_email_request(
        self,
        user: UserProtocol,
        frontend_url: Union[str, HttpUrl],
        template: TemplatePath = TemplatePath.EMAIL_EMAIL_VERIFY_TXT,
        fail_silently: bool = False,
    ) -> None:
        """
        Отправляет запрос на подтверждение почты

        :param user: Пользователь
        :param frontend_url: URL адрес frontend
        :param mail_service: Сервис по отправке email
        :param fail_silently: Не возбуждать ошибок при отправке
        :raises UserAlreadyVerified: Пользователь уже подтвердил свой email
        :raises MailServiceError: Ошибка отправки сообщения
        """

        if user.is_verified:
            raise UserAlreadyVerified

        token = self.token_generator.make_token(user, "CONFIRM")
        token_encoded = URLParser.quote_url(token)
        base_url = str(frontend_url)
        base_url = base_url.rstrip("/")
        absolute_url = f"{base_url}?token={token_encoded}"

        body = template_renderer.render_template(
            {"url": absolute_url}, template
        )

        await self.task_service.create_task(
            send_mail,
            subject="Подтверждение почты",
            body=body,
            recipients=[user.email],
            fail_silently=fail_silently,
        )

    async def verify_email(self, token: str) -> UserProtocol:
        """
        Подтверждение почты пользователя

        :param token: Токен для подтверждения
        :raises AuthInvalidToken: Невалидный токен
        :return: Обновленный пользователь
        """

        unquoted_token = URLParser.unquote_url(token)

        try:
            user_id = self.token_generator.check_token(unquoted_token)
        except InvalidToken:
            raise AuthInvalidToken("Невалидный токен подтверждения")

        async with self.uow:
            updated_user = await self.uow.users.update(
                UUID(user_id), {"is_verified": True}
            )
            await self.uow.commit()

        return updated_user

    async def reset_password_request(
        self,
        email: str,
        frontend_url: Union[str, HttpUrl],
        fail_silently: bool = False,
    ) -> None:
        """
        Отравляет ссылку для смены пароля на email пользователя

        :param email: Email телефона пользователя
        :param frontend_url: URL адреса frontend
        :param mail_service: Сервис по отправке
        :param fail_silently: Не возбуждать ошибок при отправке
        :raises UserNotExist: Такого пользователя не существует
        """

        user = await self.get_by_email(email)

        token = self.token_generator.make_token(user, "RESET")
        token_encoded = URLParser.quote_url(token)
        base_url = str(frontend_url)
        base_url = base_url.rstrip("/")
        absolute_url = f"{base_url}?token={token_encoded}"

        body = template_renderer.render_template(
            {"url": absolute_url},
            TemplatePath.EMAIL_PASSWORD_RESET_TXT,
        )

        await self.task_service.create_task(
            send_mail,
            subject="Восстановление пароля",
            body=body,
            recipients=[user.email],
            fail_silently=fail_silently,
        )

    async def reset_password(self, token: str, new_password: str) -> UserProtocol:
        """
        Проверяет токен и меняет пароль пользователя

        :param token: Токен для смены
        :param password_data: Данные о пароле
        :raises UserNotExist: Такого пользователя не существует
        :raises InvalidPassword: Пароль не валидный
        :raises AuthInvalidToken: Невалидный токен смены
        :returns: Обновленный пользователь
        """

        unquoted_token = URLParser.unquote_url(token)

        try:
            user_id = self.token_generator.check_token(unquoted_token)
        except InvalidToken:
            raise AuthInvalidToken("Невалидный токен смены")

        user = await self.get_by_id(UUID(user_id))

        await self.validate_password(new_password, user)

        new_password_hashed = self.password_helper.hash(new_password)
        async with self.uow:
            user = await self.uow.users.update(
                user.id, {"hashed_password": new_password_hashed}
            )

            await self.uow.commit()

        return user


async def get_user_verificator() -> AsyncGenerator[UserVerificator, Any]:
    yield UserVerificator()
