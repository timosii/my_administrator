import datetime as dt
from app.database.database import engine, session_maker, Base
from app.database.models.data import (
    User,
    Check,
    ViolationFound
)
from app.database.services.users import UserService
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.schemas.user_schema import UserCreate
from app.database.schemas.check_schema import CheckCreate
from app.database.schemas.violation_found_schema import ViolationFoundCreate
from loguru import logger


async def insert_data_user(user: UserService = UserService()):
    user_test_1 = UserCreate(
        id=6164463753,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 2.0',
    )
    user_test_2 = UserCreate(
        id=581145287,
        mo_='ГП 107',
        is_mo_performer=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 3.0',
    )

    user_test_3 = UserCreate(
        id=255746374,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 4.0',

    )
    
    user_test_4 = UserCreate(
        id=714806103,
        mo_='ГП 212',
        is_mo_performer=True,
        last_name='Куликов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 5.0',
    )

    user_test_5 = UserCreate(
        id=364167798,
        mo_='ГП 45',
        is_mfc=True,
        last_name='Мискарян',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 6.0',
    )

    user_test_6 = UserCreate(
        id=905290819,
        mo_='ГП 107',
        is_mo_performer=True,
        last_name='Бортников',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 7.0',
    )

    user_test_7 = UserCreate(
        id=133283796,
        mo_='ГП 45',
        is_mo_performer=True,
        last_name='Постолакин',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 8.0',
    )

    user_test_8 = UserCreate(
        id=360185080,
        mo_='ГП 212',
        is_mfc=True,
        last_name='Баум',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 9.0',
    )

    await user.add_user(user_test_1)
    await user.add_user(user_test_2)
    await user.add_user(user_test_3)
    await user.add_user(user_test_4)
    await user.add_user(user_test_5)
    await user.add_user(user_test_6)
    await user.add_user(user_test_7)
    await user.add_user(user_test_8)
    logger.info('users added to db')
