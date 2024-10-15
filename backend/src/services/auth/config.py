from src.core.config import settings
from src.services.auth.authenticator import Authenticator
from src.services.auth.backend import AuthenticationBackend
from src.services.auth.strategy import JWTStrategy
from src.services.auth.transport import BearerTransport, CookieTransport

bearer_transport = BearerTransport(token_url="auth/login")
cookie_transport = CookieTransport()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        settings.AUTH.SECRET,
        access_lifetime_seconds=settings.AUTH.JWT_ACCESS_TOKEN_LIFETIME,
        refresh_lifetime_seconds=settings.AUTH.JWT_REFRESH_TOKEN_LIFETIME,
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )


bearer_jwt_backend = AuthenticationBackend(
    name="bearer_jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
cookie_jwt_backend = AuthenticationBackend(
    name="cookie_jwt", transport=cookie_transport, get_strategy=get_jwt_strategy
)

authenticator = Authenticator([bearer_jwt_backend, cookie_jwt_backend])
