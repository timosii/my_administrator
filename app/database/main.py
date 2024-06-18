import asyncio
import datetime as dt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.models.data import User
from app.database.schemas.user_schema import UserCreate

from app.database.db_helpers.insert_users import (
    insert_data_user,   
)

from app.database.services.users import UserService

from app.database.insert_dicts.insert_dicts import DictsInsert
from app.database.insert_dicts.update_dicts import DictsUpdate

# накатить алембик сначала
DictsInsert().insert_dicts_to_db()
DictsUpdate().update_dicts_to_db()
# asyncio.get_event_loop().run_until_complete(clear_data())
asyncio.get_event_loop().run_until_complete(insert_data_user())
# asyncio.run(insert_data_user())

# drop table dicts.mos , dicts.filials , dicts.problems , dicts.violations , dicts.zones, "data"."check" , data."user" , data.violation_found cascade;
