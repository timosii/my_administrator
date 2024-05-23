import asyncio
import datetime as dt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import create_engine, URL, text
from app.config import settings
from app.database.models.data import User
from app.database.schemas.user_schema import UserCreate

from app.database.db_helpers.create_db import (
    create_tables,
)
from app.database.db_helpers.insert_data import (
    insert_data_user,
    insert_data_check,
    insert_data_violation
)
from app.database.services.users import UserService

from app.database.insert_dicts.insert_dicts import DictsInsert

# asyncio.run(create_tables())
# DictsInsert().insert_dicts_to_db()
# asyncio.run(insert_data_user())
# asyncio.run(insert_data_check())
# asyncio.run(insert_data_violation())

new_user = UserCreate(
    id=112,
    mo_='УМ ДЗМ',
    is_mfc=True,
    last_name='Тестов',
    first_name='Тест',
    patronymic='Тестович',
    post='Менеджер',
    created_at=dt.datetime.now()
    )

us_ = UserService()

asyncio.run(us_.add_user(
        user_create=new_user
        ))
# print(asyncio.run(us_.is_admin(id=112)))
# print(asyncio.run(us_.is_mfc(id=112)))
# print(asyncio.run(us_.is_mfc_leader(id=112)))
# print(asyncio.run(us_.is_mo_performer(id=112)))
# print(asyncio.run(us_.is_mo_controler(id=112)))
