import asyncio
import datetime as dt
from random import randint

from loguru import logger

from app.database.schemas.check_schema import CheckTestCreate
from app.database.schemas.violation_found_schema import ViolationFoundTestCreate
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService


class AddTestData:
    def __init__(self,
                 check_count: int,
                 violation_by_check_count: int,
                 task_count: int = 0) -> None:
        self.check_count = check_count
        self.task_count = task_count
        self.violation_by_check_count = violation_by_check_count

    async def insert_check(
            self,
            check: CheckService = CheckService()):
        current_time = dt.datetime.now(dt.timezone.utc)
        ch = CheckTestCreate(
            fil_='ГП 107',
            mfc_user_id=6164463753,
            is_task=False,
            mfc_finish=current_time
        )

        check_in = await check.add_test_check(ch)
        self.check_id = check_in.check_id

    async def insert_check_task(
            self,
            check: CheckService = CheckService()):
        current_time = dt.datetime.now(dt.timezone.utc)
        ch = CheckTestCreate(
            fil_='ГП 107',
            mfc_user_id=6164463753,
            is_task=True,
            mfc_finish=current_time
        )

        check_in = await check.add_test_check(ch)
        self.check_id = check_in.check_id

    async def insert_violation_found(
            self,
            violation_found: ViolationFoundService = ViolationFoundService()
    ):
        current_time = dt.datetime.now(dt.timezone.utc)
        check_id = self.check_id
        violation_dict_id = randint(1, 110)
        v = ViolationFoundTestCreate(
            check_id=check_id,
            violation_dict_id=violation_dict_id,
            photo_id_mfc='AgACAgIAAxkBAAIWaWZzYejf5TuIjTY6k33RG5VXuGnrAALA2jEbxrmYSzsZCXXhT3thAQADAgADeQADNQQ',
            comm_mfc=f'TEST_VIOLATION_{violation_dict_id}',
            violation_detected=current_time
        )
        violation_found_in = await violation_found.add_test_violation(v)
        logger.info(f'TEST_VIOLATION_FOUND_ID {violation_found_in.violation_found_id} ADDED')

    async def add_checks(
            self,

    ):
        check_count = self.check_count
        violation_count = self.violation_by_check_count
        for check in range(check_count):
            await atd.insert_check()
            for violation in range(violation_count):
                await atd.insert_violation_found()


if __name__ == '__main__':
    atd = AddTestData(check_count=4, violation_by_check_count=3)
    asyncio.get_event_loop().run_until_complete(atd.add_checks())
