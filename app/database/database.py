import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings

class Base(DeclarativeBase):
    repr_cols_num = 5
    repr_cols = tuple()

    def __repr__(self) -> str:
         cols = []
         for idx, col in enumerate(self.__table__.columns.keys()):
             if col in self.repr_cols or idx < self.repr_cols_num:
                 cols.append(f"{col} = {getattr(self, col)}")
         return f"<{self.__class__.__name__} {', '.join(cols)}>"


engine = create_async_engine(
    url= settings.url_constructor,
    echo=True,
    # pool_size=5,
    # max_overflow=10
)

session_maker = async_sessionmaker(engine)