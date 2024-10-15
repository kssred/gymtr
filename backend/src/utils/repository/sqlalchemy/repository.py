from collections.abc import Sequence
from typing import Any, Generic, Literal, NamedTuple, Optional, TypeVar

from sqlalchemy import Select, delete, func, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import (
    DBAPIError,
)
from sqlalchemy.exc import (
    IntegrityError as IntegrityErrorSA,
)
from sqlalchemy.exc import (
    MultipleResultsFound as MultipleResultsFoundSA,
)
from sqlalchemy.exc import (
    NoResultFound as NoResultFoundSA,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.types import ID
from src.database import BaseModel, async_session_maker
from src.utils.repository.base import MODEL, RepositoryABC
from src.utils.repository.exceptions import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    RepositoryException,
)

SELECT_TYPE = TypeVar("SELECT_TYPE", bound=tuple)
BASE_MODEL = TypeVar("BASE_MODEL", covariant=True, bound=BaseModel)


class PaginatedTuple(NamedTuple, Generic[SELECT_TYPE]):
    query: Select[SELECT_TYPE]
    total_count: int


class SQLAlchemyRepository(RepositoryABC[MODEL, ID]):
    model: type[BASE_MODEL]

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def get(self, **filters) -> MODEL:
        query = select(self.model).filter_by(**filters)
        try:
            result = await self.session.execute(query)
        except DBAPIError as e:
            raise RepositoryException from e

        try:
            return result.scalar_one()
        except MultipleResultsFoundSA as e:
            raise MultipleResultsFound from e
        except NoResultFoundSA as e:
            raise NoResultFound from e

    async def get_or_none(self, **filters) -> Optional[MODEL]:
        try:
            return await self.get(**filters)
        except (NoResultFound, MultipleResultsFound):
            return None

    async def get_by_id(self, id_: ID) -> MODEL:
        result = await self.get(id=id_)
        return result

    async def exists(self, **filters) -> bool:
        query = select(1).select_from(self.model).filter_by(**filters)

        result = await self.session.execute(query)

        return bool(result.scalars().first())

    async def find_all(self) -> list[MODEL]:
        query = select(self.model)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def filter(self, **filters) -> list[MODEL]:
        query = select(self.model).filter_by(**filters)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def bulk_create(
        self,
        data: Sequence[dict[str, Any]],
        on_conflict: Optional[Literal["do_nothing"]] = None,
        index_elements: Optional[Sequence[str]] = None,
        render_nulls: bool = False,
        **kwargs,
    ) -> None:
        # render_nulls - обязует проставлять необязательные поля в None. Но в таком случае server_default слетают

        stmt = insert(self.model).execution_options(render_nulls=render_nulls)
        if on_conflict:
            stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)

        try:
            await self.session.execute(stmt, data)
        except IntegrityErrorSA as e:
            raise IntegrityError(error_info=e.orig.args[0]) from e
        except DBAPIError as e:
            raise RepositoryException("Ошибка при добавлении") from e

    async def create(self, data: dict[str, Any], **kwargs) -> MODEL:
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            result = await self.session.execute(stmt)
        except IntegrityErrorSA as e:
            raise IntegrityError(error_info=e.orig.args[0]) from e
        except DBAPIError as e:
            raise RepositoryException("Ошибка при добавлении") from e

        return result.scalar_one()

    async def create_or_update(
        self,
        data: Sequence[dict[str, Any]],
        index_elements: Sequence[str],
        returning: Optional[Sequence[str]] = None,
        render_nulls: bool = False,
        **kwargs,
    ) -> Sequence:
        returning_cols = (
            [getattr(self.model, ret_col) for ret_col in returning]
            if returning
            else self.model
        )

        stmt = insert(self.model).values(data)
        update_columns = {
            column.name: stmt.excluded[column.name]
            for column in self.model.__table__.columns
            if column.name not in ["id", "created_at"]
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=update_columns,
        ).returning(*returning_cols)

        try:
            result = await self.session.execute(stmt)
        except DBAPIError as e:
            raise RepositoryException from e

        return result.all()

    async def update_by_filters(self, data: dict[str, Any], **filters) -> list[MODEL]:
        stmt = (
            update(self.model).filter_by(**filters).values(**data).returning(self.model)
        )

        try:
            result = await self.session.execute(stmt)
        except NoResultFoundSA as e:
            raise NoResultFound from e
        except IntegrityErrorSA as e:
            raise IntegrityError(error_info=e.orig.args[0]) from e
        except DBAPIError as e:
            raise RepositoryException("Ошибка при обновлении") from e

        return list(result.scalars().all())

    async def update(self, record_id: ID, data: dict[str, Any], **kwargs) -> MODEL:
        stmt = (
            update(self.model)
            .filter_by(id=record_id)
            .values(**data)
            .returning(self.model)
        )

        try:
            result = await self.session.execute(stmt)
        except IntegrityErrorSA as e:
            raise IntegrityError(error_info=e.orig.args[0]) from e
        except DBAPIError as e:
            raise RepositoryException("Ошибка при обновлении") from e

        try:
            return result.scalar_one()
        except MultipleResultsFoundSA as e:
            raise MultipleResultsFound from e
        except NoResultFoundSA as e:
            raise NoResultFound from e

    async def delete(self, record_id: ID, **kwargs) -> int:
        stmt = delete(self.model).filter_by(id=record_id).returning(self.model)
        result = await self.session.execute(stmt)
        try:
            return len(result.one())
        except NoResultFoundSA as e:
            raise NoResultFound from e
        except MultipleResultsFoundSA as e:
            raise MultipleResultsFound from e

    async def bulk_delete_by_filter(self, **filters) -> int:
        stmt = delete(self.model).filter_by(**filters).returning(self.model)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def bulk_delete_by_ids(self, records_ids: list[ID]) -> int:
        stmt = (
            delete(self.model)
            .where(self.model.id.in_(records_ids))
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def paginate_query(
        self,
        query: Select[SELECT_TYPE],
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedTuple[SELECT_TYPE]:
        count_query = select(func.count()).select_from(query.subquery())
        count = await self.session.execute(count_query)
        count = count.scalar_one()

        paginated_query = query.limit(limit).offset(offset)

        return PaginatedTuple(query=paginated_query, total_count=count)

    @classmethod
    async def check_connection(cls) -> None:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
