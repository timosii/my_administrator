#!/usr/bin/python
import asyncio
import os

from loguru import logger

from app.config import settings
from app.main import start_bot, start_local


def set_logger_config():
    log_path = os.path.join('logs/debug.log')
    logger.add(
        log_path,
        format='{time} | {level} | {module}:{function}:{line} | {message}',
        level='DEBUG',
        rotation='200 KB',
        compression='zip',
    )


def main():
    set_logger_config()
    if settings.IS_TEST:
        asyncio.run(start_local())
    else:
        start_bot()


if __name__ == '__main__':
    main()
