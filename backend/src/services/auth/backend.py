from fastapi import Response, status

from src.core.types.user import UserProtocol
from src.services.auth.strategy import StrategyABC, StrategyDestroyNotSupportedError
from src.services.auth.transport import TransportABC, TransportLogoutNotSupportedError
from src.typing import DependencyCallable


class AuthenticationBackend:
    """
    Комбинация стратегии аутентификации и транспорта токена.
    Вместе они воплощают всю логику аутентификации
    """

    name: str
    transport: TransportABC

    def __init__(
        self,
        name: str,
        transport: TransportABC,
        get_strategy: DependencyCallable[StrategyABC],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(self, strategy: StrategyABC, user: UserProtocol) -> Response:
        access_token, refresh_token = await strategy.write_token(user)
        return await self.transport.get_login_response(access_token, refresh_token)

    async def logout(
        self, strategy: StrategyABC, user: UserProtocol, token: str
    ) -> Response:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass

        try:
            response = await self.transport.get_logout_response()
        except TransportLogoutNotSupportedError:
            response = Response(status_code=status.HTTP_204_NO_CONTENT)

        return response
