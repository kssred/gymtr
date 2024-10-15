from fastapi import APIRouter

from src.api.v1.endpoints import user
from src.api.v1.endpoints.auth import auth, email, password

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(email.router, prefix="/user/email", tags=["user"])
api_router.include_router(password.router, prefix="/user/password", tags=["user"])
api_router.include_router(user.router, prefix="/user/profile", tags=["user"])
