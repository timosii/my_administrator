import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database.services.check import CheckService
from app.utils.data_save_process import scheduler_download_photos

scheduler = AsyncIOScheduler()
scheduler.add_job(CheckService().scheduler_unfinished_checks_process, CronTrigger(hour=23, minute=59))
scheduler.add_job(scheduler_download_photos, CronTrigger(hour=22, minute=59))


if __name__ == '__main__':
    asyncio.run(CheckService().scheduler_unfinished_checks_process())
    asyncio.run(scheduler_download_photos())
