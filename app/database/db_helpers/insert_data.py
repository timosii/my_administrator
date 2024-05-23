import datetime as dt
from app.database.database import engine, session_maker, Base
from app.database.models.data import (
    User,
    Check,
    ViolationFound
)


async def insert_data_user():
    async with session_maker() as session:
        user_test = User(
            id=581145287,
            mo_='ДГП 69',
            is_admin=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик',
            created_at=dt.datetime.now()
            )
        user_test_2 = User(
            id=111,
            mo_='ГП 107',
            is_mfc=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 2.0',
            created_at=dt.datetime.now()
        )
        session.add_all([user_test, user_test_2])       
        await session.commit()

async def insert_data_check():
    async with session_maker() as session:
        check_test_1 = Check(
            fil_='ДГП 69 филиал 2',
            user_id = 581145287,
            mfc_start=dt.datetime.now(),
        )
        check_test_2 = Check(
            fil_='ГП 107',
            user_id = 111,
            mfc_start=dt.datetime.now(),
        )
        session.add_all([check_test_1, check_test_2])       
        await session.commit()

async def insert_data_violation():
    async with session_maker() as session:
        vio_test_1 = ViolationFound(
            check_id=1,
            violation_id=3,
            violation_detected=dt.datetime.now(),
            photo_id='test',
            comm='testtest',
        )
        vio_test_2 = ViolationFound(
            check_id=1,
            violation_id=33,
            violation_detected=dt.datetime.now(),
            photo_id='test',
            comm='testtest',
        )
        session.add_all([vio_test_1, vio_test_2])       
        await session.commit()


