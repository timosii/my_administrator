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
from app.database.schemas.user_schema import UserCreate, UserUpdate
from app.database.schemas.check_schema import CheckCreate
from app.database.schemas.violation_found_schema import ViolationFoundCreate
from loguru import logger


async def insert_data_user(user: UserService = UserService()):
    user_tests = [
        UserCreate(
            user_id=6164463753,
            is_mfc=True,
            last_name='Симашев',
            first_name='Тест',
        ),
        UserCreate(
            user_id=581145287,
            mo_='ГП 107',
            fil_='ГП 107',
            is_mo_performer=True,
            last_name='Симашев',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=255746374,
            is_mfc=True,
            last_name='Тестов',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=714806103,
            is_mfc=True,
            last_name='Куликов',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=364167798,
            is_mfc=True,
            last_name='Мискарян',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=905290819,
            mo_='ГП 3',
            fil_='ГП 3 филиал 2',
            is_mo_performer=True,
            last_name='Бортников',
            first_name='Василий',
            patronymic='Павлович',
        ),
        UserCreate(
            user_id=133283796,
            is_mfc=True,
            last_name='Постолакин',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=360185080,
            is_mfc=True,
            last_name='Баум',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=322561217,
            is_mfc=True,
            last_name='Варлашин',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=153964237,
            is_mfc=True,
            last_name='Сизов',
            first_name='Тест',
            patronymic='Тестович',
        ),
        UserCreate(
            user_id=779416588,
            is_mfc=True,
            last_name='Бортникова',
            first_name='София',
            patronymic='Петровна',
        ),
        UserCreate(
            user_id=1064558495,
            is_mfc=True,
            last_name='Цеховский',
            first_name='Антон',
            patronymic='Валерьевич',
        ),
        UserCreate(
            user_id=758493610,
            is_mfc=True,
            last_name='Учава',
            first_name='Мария',
            patronymic='Георгиевна',
        ),
        UserCreate(
            user_id=5295764195,
            is_mfc=True,
            last_name='Маркушина',
            first_name='Яна',
            patronymic='Андреевна',
        ),
        UserCreate(
            user_id=769695577,
            is_mfc=True,
            last_name='Стецкая',
            first_name='Нина',
            patronymic='Владимировна',
        ),
        UserCreate(
            user_id=1451698229,
            is_mfc=True,
            last_name='Соседова',
            first_name='Лариса',
            patronymic='Николаевна',
        ),
        UserCreate(
            user_id=6222915758,
            is_mfc=True,
            last_name='Айнетдинова',
            first_name='Альфинур',
            patronymic='Надировна',
        ),
        UserCreate(
            user_id=596817016,
            is_mfc=True,
            last_name='Кирсанова',
            first_name='Валерия',
            patronymic='Максимовна',
        ),
        UserCreate(
            user_id=1674412984,
            is_mfc=True,
            last_name='Бедретдинова',
            first_name='Динара',
            patronymic='Тагировна',
        ),
        UserCreate(
            user_id=718701209,
            is_mfc=True,
            last_name='Беличенко',
            first_name='Екатерина',
            patronymic='Геннадьевна',
        ),
        UserCreate(
            user_id=639408037,
            is_mfc=True,
            last_name='Савков',
            first_name='Михаил',
            patronymic='Игоревич',
        ),
        UserCreate(
            user_id=5656901854,
            is_mfc=True,
            last_name='Смирнова',
            first_name='Наталия',
            patronymic='Игоревна',
        ),
        UserCreate(
            user_id=5082842523,
            is_mfc=True,
            last_name='Аксёнова',
            first_name='Светлана',
            patronymic='Михайловна',
        ),
        UserCreate(
            user_id=5247413307,
            is_mfc=True,
            last_name='Лепих',
            first_name='Надежда',
            patronymic='Евгеньевна',
        ),
        UserCreate(
            user_id=436270994,
            is_mfc=True,
            last_name='Ларионова',
            first_name='Александра',
            patronymic='Павловна',
        ),
        UserCreate(
            user_id=498442469,
            is_mfc=True,
            last_name='Щеглова',
            first_name='Анастасия',
            patronymic='Андреевна',
        ),
        UserCreate(
            user_id=1127003728,
            is_mfc=True,
            last_name='Гаряева',
            first_name='Надия',
            patronymic='Никитична',
        ),
        UserCreate(
            user_id=967022472,
            is_mfc=True,
            last_name='Горячкина',
            first_name='Дарья',
            patronymic='Сергеевна',
        ),
        UserCreate(
            user_id=6169285233,
            is_mfc=True,
            last_name='Баженова',
            first_name='Олеся',
            patronymic='Алексеевна',
        ),
        UserCreate(
            user_id=755250036,
            is_mfc=True,
            last_name='Таилкина',
            first_name='Екатерина',
            patronymic='Игоревна',
        ),
        UserCreate(
            user_id=1394056504,
            mo_='ГП 68',
            fil_='ГП 68 филиал 1',
            is_mo_performer=True,
            last_name='Сугробова',
            first_name='Екатерина',
        ),
        UserCreate(
            user_id=1902811478,
            mo_='ГП 68',
            fil_='ГП 68 филиал 1',
            is_mo_performer=True,
            last_name='Алпатова',
            first_name='Ксения',
        ),
        UserCreate(
            user_id=1768782274,
            mo_='ДГП 38',
            fil_='ДГП 38 филиал 3',
            is_mo_performer=True,
            last_name='Меркулова',
            first_name='Анастасия',
            patronymic='Сергеевна',
        ),
        UserCreate(
            user_id=5134496671,
            mo_='ДГП 38',
            fil_='ДГП 38 филиал 3',
            is_mo_performer=True,
            last_name='Головинова',
            first_name='Елена',
        ),
        UserCreate(
            user_id=1111228999,
            mo_='ГП 3',
            fil_='ГП 3 филиал 2',
            post='Заведующий филиалом',
            is_mo_performer=True,
            last_name='Самсонов',
            first_name='Сергей',
            patronymic='Вячеславович',
        ),
        UserCreate(
            user_id=1978285089,
            mo_='ГП 3',
            fil_='ГП 3 филиал 2',
            post='Старшая медицинская сестра',
            is_mo_performer=True,
            last_name='Патрикеева',
            first_name='Светлана',
        ),
    ]

    for u in user_tests:
        existing_user = await user.user_exists(u.user_id)
        if not existing_user:
            await user.add_user(u)    
        else:
            current_user = await user.get_user_by_id(u.user_id)
            fields_changed = any(
                getattr(u, field) != getattr(current_user, field)
                for field in u.__dict__
                if field != 'user_id'
            )
            if fields_changed:
                user_update = UserUpdate(**u.model_dump(exclude={'user_id'}))
                await user.update_user(user_id=u.user_id, user_update=user_update)
                logger.info(f'User with id {u.user_id} updated in db')
            else:
                logger.info(f'User with id {u.user_id} already exists in db and no fields have changed')
    
    logger.info('users process finished')


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