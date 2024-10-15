from typing import Annotated

from fastapi import Depends

from src.core.types.user import UserProtocol
from src.services.auth import (
    UserService,
    UserVerificator,
    get_user_service,
    get_user_verificator,
)
from src.services.auth.config import authenticator
from src.services.mail import EmailService, get_email_service

get_optional_user = authenticator.current_user(optional=True)
get_current_user = authenticator.current_user(active=True)
get_refresh_user = authenticator.current_user(active=True, refresh=True)

# Services
UserServiceDependency = Annotated[UserService, Depends(get_user_service)]
UserVerificatorDependency = Annotated[UserVerificator, Depends(get_user_verificator)]
EmailServiceDependency = Annotated[EmailService, Depends(get_email_service)]

# Auth
OptionalUserDependency = Annotated[UserProtocol, Depends(get_optional_user)]
CurrentUserDependency = Annotated[UserProtocol, Depends(get_current_user)]
RefreshUserDependency = Annotated[UserProtocol, Depends(get_refresh_user)]

# Other
