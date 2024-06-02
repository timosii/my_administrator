import os
from loguru import logger
from aiogram.types import User, Message

class Logger:
    
    start = "bot started"
    stop = "bot stopped"
    
    @property
    def set_config(self):
        log_path = os.path.join(("logs/debug.log"))
        logger.add(
            log_path,
            format="{time} | {level} | {module}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="100 KB",
            compression="zip",
        )

    def passed_authorization(user: User):
        return f"User {user.id} ({user.username}) passed authorization"

    def log_error(user: User, e: Exception):
        return f"Error occurred for user {user.id} ({user.username}): {e}"
