from typing import Optional

from jwt import PyJWTError

from src.core.config import settings
from src.core.types.user import UserProtocol
from src.services.auth.jwt_shortcuts import SecretType, decode_jwt, generate_jwt
from src.services.auth.strategy import StrategyABC, StrategyDestroyNotSupportedError


class JWTStrategy(StrategyABC):
    def __init__(
        self,
        secret: SecretType,
        access_lifetime_seconds: Optional[int],
        refresh_lifetime_seconds: Optional[int],
        token_audience: Optional[list[str]] = None,
        algorithm: str = "HS256",
        public_key: Optional[SecretType] = None,
    ):
        if not token_audience:
            token_audience = [f"{settings.PROJECT_NAME}:auth"]
        self.secret = secret
        self.access_lifetime_seconds = access_lifetime_seconds
        self.refresh_lifetime_seconds = refresh_lifetime_seconds
        self.token_audience = token_audience
        self.algorithm = algorithm
        self.public_key = public_key

    @property
    def encode_key(self) -> SecretType:
        return self.secret

    @property
    def decode_key(self) -> SecretType:
        return self.public_key or self.secret

    async def read_token(
        self,
        token: Optional[str],
        refresh: bool,
    ) -> Optional[dict]:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token, self.decode_key, self.token_audience, algorithms=[self.algorithm]
            )
            user_id = data.get("sub")
            if user_id is None:
                return None
        except PyJWTError:
            return None

        token_type = data.get("token_type")
        if refresh and token_type != "refresh":
            return None
        elif not refresh and token_type == "refresh":
            return None

        return data

    async def write_token(
        self, user: UserProtocol, **kwargs
    ) -> tuple[str, Optional[str]]:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
        }

        data["token_type"] = "access"
        access_token = generate_jwt(
            data,
            self.encode_key,
            self.access_lifetime_seconds,
            algorithm=self.algorithm,
        )
        data["token_type"] = "refresh"
        refresh_token = generate_jwt(
            data,
            self.encode_key,
            self.refresh_lifetime_seconds,
            algorithm=self.algorithm,
        )
        return access_token, refresh_token

    async def destroy_token(self, token: str, user: UserProtocol) -> None:
        raise StrategyDestroyNotSupportedError
