import datetime as dt
from typing import Annotated

from sqlalchemy import BigInteger, String, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column

from app.config import settings

engine = create_async_engine(
    url=settings.url_constructor,
)

session_maker = async_sessionmaker(engine)

intpk = Annotated[int, mapped_column(
    primary_key=True,
    autoincrement=False,
)]
bigint_pk = Annotated[int, mapped_column(
    primary_key=True,
    type_=BigInteger
)]
bigint_pk_tg = Annotated[int, mapped_column(
    primary_key=True,
    autoincrement=False,
    type_=BigInteger
)]
bigint = Annotated[int, mapped_column(
    type_=BigInteger
)]
str_pk = Annotated[str, mapped_column(
    primary_key=True,
    type_=String(255)
)]
str_255 = Annotated[str, mapped_column(
    type_=String(255)
)]
datetime_now = Annotated[dt.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[dt.datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=text("TIMEZONE('utc', now())"),
)]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols: tuple = tuple()

    def __repr__(self) -> str:
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f'{col} = {getattr(self, col)}')
        return f"<{self.__class__.__name__} {', '.join(cols)}>"
