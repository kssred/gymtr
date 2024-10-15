from pydantic import Field

from src.schemas.base import BaseSchema


class PaginationQueryParams(BaseSchema):
    """Схема для пагинации ответа, от неё наследовать все схемы, где необходима пагинация"""

    page: int = Field(1)
    page_size: int = Field(50, le=100)

    def get_limit_offset(self) -> tuple[int, int]:
        limit = self.page_size
        offset = (self.page - 1) * limit
        return limit, offset
