from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    Integer,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import mapped_column

from src.utils.clock import Clock

# ID
smallint_pk = Annotated[
    int, mapped_column(SmallInteger, Identity(always=True), primary_key=True)
]
int_pk = Annotated[int, mapped_column(Integer, Identity(always=True), primary_key=True)]
bigint_pk = Annotated[
    int, mapped_column(BigInteger, Identity(always=True), primary_key=True)
]
uuid_pk = Annotated[
    UUID, mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
]

# Strings
str_50 = Annotated[str, mapped_column(String(50), nullable=False)]
str_100 = Annotated[str, mapped_column(String(100), nullable=False)]
str_200 = Annotated[str, mapped_column(String(200), nullable=False)]
str_255 = Annotated[str, mapped_column(String(255), nullable=False)]
text_1500 = Annotated[str, mapped_column(String(length=1500), nullable=False)]

# Date, time
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime, server_default=text("TIMEZONE('utc', now())"), comment="Создан"
    ),
]
updated_at = Annotated[
    datetime,
    mapped_column(
        DateTime,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=Clock.utc_now,
        comment="Изменён",
    ),
]
