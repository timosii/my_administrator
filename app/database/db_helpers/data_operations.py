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
        user_id=6164463753,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 2.0',
    )
    user_test_2 = UserCreate(
        user_id=581145287,
        mo_='ГП 107',
        is_mo_performer=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 3.0',
    )

    user_test_3 = UserCreate(
        user_id=255746374,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 4.0',

    )
    
    user_test_4 = UserCreate(
        user_id=714806103,
        mo_='ГП 212',
        is_mo_performer=True,
        last_name='Куликов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 5.0',
    )

    user_test_5 = UserCreate(
        user_id=364167798,
        mo_='ГП 45',
        is_mfc=True,
        last_name='Мискарян',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 6.0',
    )

    user_test_6 = UserCreate(
        user_id=905290819,
        mo_='ГП 107',
        is_mo_performer=True,
        last_name='Бортников',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 7.0',
    )

    user_test_7 = UserCreate(
        user_id=133283796,
        mo_='ГП 45',
        is_mo_performer=True,
        last_name='Постолакин',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 8.0',
    )

    user_test_8 = UserCreate(
        user_id=360185080,
        mo_='ГП 212',
        is_mfc=True,
        last_name='Баум',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 9.0',
    )

    user_test_9 = UserCreate(
        user_id=322561217,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Варлашин',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 10.0',

    )
    for u in (
        user_test_1,
        user_test_2,
        user_test_3,
        user_test_4,
        user_test_5,
        user_test_6,
        user_test_7,
        user_test_8,
        user_test_9
    ):
        await user.add_user(u)    
    logger.info('users added to db')


async def clear_data(
        user: UserService=UserService(),
        check: CheckService=CheckService(),
        violations_found: ViolationFoundService=ViolationFoundService()
        ):
    await violations_found.delete_all_violations_found()
    logger.info('violations found deleted')
    await check.delete_all_checks()
    logger.info('checks deleted')
    await user.delete_all_users()
    logger.info('users deleted')