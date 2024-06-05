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
from loguru import logger


async def clear_data(
        user: UserService=UserService(),
        check: CheckService=CheckService(),
        violations_found: ViolationFoundService=ViolationFoundService()
        ):
    await user.delete_all_users()
    await check.delete_all_checks()
    await violations_found.delete_all_violations_found()
