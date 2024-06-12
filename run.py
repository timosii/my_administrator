#!/usr/bin/python
import sys
import asyncio
import os
from app.main import start_bot
from loguru import logger


def set_logger_config():
    log_path = os.path.join(("logs/debug.log"))
    logger.add(
        log_path,
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="100 KB",
        compression="zip",
    )


def main():
    set_logger_config()
    # asyncio.get_event_loop().run_until_complete(start_bot())
    start_bot()
    # asyncio.get_event_loop().run_forever()
    # asyncio.run(start_bot())


if __name__ == "__main__":
    main()
