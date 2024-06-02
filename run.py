#!/usr/bin/python
import sys
import asyncio
import os
from app.main import start_bot
from app.logger_config import Logger, logger


@logger.catch
def main():
    Logger().set_config
    asyncio.run(start_bot())


if __name__ == "__main__":
    main()
