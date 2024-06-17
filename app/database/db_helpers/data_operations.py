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
    user_tests = [
        UserCreate(
            user_id=6164463753,
            # mo_='ГП 107',
            is_mfc=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 2.0',
        ),
        UserCreate(
            user_id=581145287,
            mo_='ГП 107',
            fil_='ГП 107',
            is_mo_performer=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 3.0',
        ),
        UserCreate(
            user_id=255746374,
            # mo_='ГП 107',
            is_mfc=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 4.0',
        ),
        UserCreate(
            user_id=714806103,
            # mo_='ГП 212',
            is_mfc=True,
            last_name='Куликов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 5.0',
        ),
        UserCreate(
            user_id=364167798,
            # mo_='ГП 45',
            is_mfc=True,
            last_name='Мискарян',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 6.0',
        ),
        UserCreate(
            user_id=905290819,
            mo_='ДГП 38',
            fil_='ДГП 38 филиал 3',
            is_mo_performer=True,
            last_name='Бортников',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 7.0',
        ),
        UserCreate(
            user_id=133283796,
            # mo_='ГП 45',
            is_mfc=True,
            last_name='Постолакин',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 8.0',
        ),
        UserCreate(
            user_id=360185080,
            # mo_='ГП 212',
            is_mfc=True,
            last_name='Баум',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 9.0',
        ),
        UserCreate(
            user_id=322561217,
            # mo_='ГП 107',
            is_mfc=True,
            last_name='Варлашин',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 10.0',
        ),
        UserCreate(
            user_id=153964237,
            # mo_='ГП 107',
            is_mfc=True,
            last_name='Сизов',
            first_name='Тест',
            patronymic='Тестович',
            post='Аналитик 11.0',
        ),
        UserCreate(
            user_id=779416588,
            # mo_='ГП 107',
            is_mfc=True,
            last_name='Бортникова',
            first_name='Соня',
            patronymic='Тестовна',
            post='Жена',
        ),
    ]

    for u in user_tests:
        existing_user = await user.user_exists(u.user_id)
        if not existing_user:
            await user.add_user(u)    
        else:
            logger.info(f'User with id {u.user_id} already exists in db')
    
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