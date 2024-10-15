from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database import async_session_maker
from src.repository import UserRepository

from .base import UoWABC


class SQLAlchemyUoW(UoWABC):
    def __init__(
        self, session_maker: async_sessionmaker[AsyncSession] = async_session_maker
    ) -> None:
        self.session_maker = session_maker

    async def __aenter__(self):
        self.session = self.session_maker()
        self.users = UserRepository(self.session)

        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
