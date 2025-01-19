import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database.services.check import CheckService

scheduler_unfinished_checks = AsyncIOScheduler()
scheduler_unfinished_checks.add_job(CheckService().scheduler_unfinished_checks_process, CronTrigger(hour=23, minute=59))

if __name__ == '__main__':
    asyncio.run(CheckService().scheduler_unfinished_checks_process())
