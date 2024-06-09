import asyncio
import datetime as dt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.models.data import User
from app.database.schemas.user_schema import UserCreate

from app.database.db_helpers.data_operations import (
    insert_data_user,
    clear_data
)
from app.database.services.users import UserService

from app.database.insert_dicts.insert_dicts import DictsInsert

# накатить алембик сначала
# DictsInsert().insert_dicts_to_db()
# asyncio.run(clear_data())
asyncio.run(insert_data_user())
# asyncio.get_event_loop().run_until_complete(insert_data_user())

# drop table dicts.mos , dicts.filials , dicts.problems , dicts.violations , dicts.zones, "data"."check" , data."user" , data.violation_found cascade;
