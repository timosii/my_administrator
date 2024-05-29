import asyncio
import datetime as dt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.models.data import User
from app.database.schemas.user_schema import UserCreate

# from app.database.db_helpers.create_db import (
#     create_tables,
# )
from app.database.db_helpers.insert_data import (
    insert_data_user,
    insert_data_check,
    insert_data_violation
)
from app.database.services.users import UserService

from app.database.insert_dicts.insert_dicts import DictsInsert

# asyncio.run(create_tables())
DictsInsert().insert_dicts_to_db()
asyncio.run(insert_data_user())
# asyncio.run(insert_data_check())
# asyncio.run(insert_data_violation())

# drop table dicts.mos , dicts.filials , dicts.problems , dicts.violations , dicts.zones, "data"."check" , data."user" , data.violation_found cascade;