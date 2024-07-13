import asyncio

from loguru import logger

from app.database.services.check import CheckService
from app.database.services.users import UserService
from app.database.services.violations_found import ViolationFoundService


async def clear_data(
        user: UserService = UserService(),
        check: CheckService = CheckService(),
        violations_found: ViolationFoundService = ViolationFoundService()
):
    await check.delete_all_checks()
    logger.info('checks deleted')
    await violations_found.delete_all_violations_found()
    logger.info('violations found deleted')
    await user.delete_all_users()
    logger.info('users deleted')


async def clear_checks_cascade(
        check: CheckService = CheckService(),
):
    await check.delete_all_checks()
    logger.info('checks deleted')


if __name__ == '__main__':
    asyncio.run(clear_checks_cascade())
