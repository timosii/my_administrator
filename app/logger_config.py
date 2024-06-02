import os
from loguru import logger
from aiogram.types import User, Message

class Logger:
    def __init__(self) -> None:
        self.logger = logger
    
    @property
    def set_config(self):
        log_path = os.path.join(("logs/debug.log"))
        self.logger.add(
            log_path,
            format="{time} | {level} | {module}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="100 KB",
            compression="zip",
        )
    
    @property
    def start(self):
        self.logger.info("bot started")

    @property
    def stop(self):
        self.logger.info("bot stopped")

    def passed_authorization(self, user: User):
        self.logger.info(f"User {user.id} ({user.username}) passed authorization")

    def log_error(self, user: User, e: Exception):
        self.logger.error(f"Error occurred for user {user.id} ({user.username}): {e}")
