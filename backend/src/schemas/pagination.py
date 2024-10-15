from math import ceil
from typing import Generic, Sequence

from pydantic import Field, computed_field

from src.schemas.base import BASE_SCHEMA, BaseSchema


class PaginationSchema(BaseSchema, Generic[BASE_SCHEMA]):
    count: int
    page_size: int = Field(..., exclude=True)
    results: Sequence[BASE_SCHEMA]

    @computed_field
    @property
    def num_pages(self) -> int:
        return ceil(self.count / self.page_size)


def get_paginate_schema(
    total_count: int, page_size: int, results: Sequence[BASE_SCHEMA]
) -> PaginationSchema[BASE_SCHEMA]:
    """Превратить результативную схему в Pagination схему"""

    return PaginationSchema(count=total_count, page_size=page_size, results=results)
