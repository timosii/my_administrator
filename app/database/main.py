import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.methods.create_db import (
    create_tables,
)
from app.database.methods.insert_data import (
    insert_data_user,
    insert_data_check,
    insert_data_violation
)

from app.database.insert_dicts.insert_dicts import DictsInsert

asyncio.run(create_tables())
DictsInsert().insert_dicts_to_db()
# asyncio.run(insert_data_user())
# asyncio.run(insert_data_check())
# asyncio.run(insert_data_violation())
