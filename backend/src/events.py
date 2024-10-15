from src.utils.repository.redis import RedisRepository
from src.utils.repository.sqlalchemy import SQLAlchemyRepository


async def check_db_connection():
    await SQLAlchemyRepository.check_connection()
    await RedisRepository.check_connection()
