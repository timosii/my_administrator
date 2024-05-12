import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy import create_engine, URL, text
from app.config import settings

Base = declarative_base()

engine = create_async_engine(
    url= settings.url_constructor,
    echo=True,
    # pool_size=5,
    # max_overflow=10
)

session_maker = async_sessionmaker(engine)