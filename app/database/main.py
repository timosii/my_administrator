import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from crud import (
    create_tables,
    # insert_data
)

asyncio.run(create_tables())
# asyncio.run(insert_data())