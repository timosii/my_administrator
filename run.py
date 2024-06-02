#!/usr/bin/python
import sys
import asyncio
import os
from loguru import logger
from app.main import start_bot


@logger.catch
def main():
    log_path = os.path.join(("logs/debug.log"))
    logger.add(
        log_path,
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="100 KB",
        compression="zip",
    )
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
