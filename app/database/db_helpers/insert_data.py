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



async def insert_data_user(user: UserService = UserService()):
    user_test_1 = UserCreate(
        id=6164463753,
        mo_='ГП 175',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 2.0',
    )
    user_test_2 = UserCreate(
        id=581145287,
        mo_='ГП 107',
        is_mfc=True,
        last_name='Тестов',
        first_name='Тест',
        patronymic='Тестович',
        post='Аналитик 3.0',
    )
    
    await user.add_user(user_test_1)
    await user.add_user(user_test_2)

async def insert_data_check(check: CheckService = CheckService()):
    check_test_1 = CheckCreate(
        fil_='ГП 175 филиал 1',
        user_id = 6164463753,
    )
    check_test_2 = CheckCreate(
        fil_='ГП 107 филиал 2',
        user_id = 581145287,
    )
    await check.add_check(check_test_1)
    await check.add_check(check_test_2)


async def insert_data_violation(violation: ViolationFoundService = ViolationFoundService()):
    vio_test_1 = ViolationFoundCreate(
        check_id=1,
        violation_id=13,
        photo_id='test',
        comm='testtest',
    )
    vio_test_2 = ViolationFoundCreate(
        check_id=2,
        violation_id=34,
        photo_id='test',
        comm='testtest',
    )

    await violation.add_violation(vio_test_1)
    await violation.add_violation(vio_test_2)

