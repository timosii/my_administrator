import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.methods.create_db import (
    create_tables,
    # insert_data
)
from app.database.insert_dicts.insert_dicts import DictsInsert

asyncio.run(create_tables())
asyncio.run(DictsInsert().insert_to_db())
# asyncio.run(insert_data())