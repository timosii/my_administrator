from aiogram import Dispatcher
from aiogram.types import TelegramObject, Message, CallbackQuery, User
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from loguru import logger
from app.logger_config import Logger
from typing import Callable, Dict, Any, Awaitable

class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject, 
            data: Dict[str, Any]
            ) -> Any:
        user: User = data.get('event_from_user')
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(Logger.log_error(user=user, e=e))
            raise e
        
