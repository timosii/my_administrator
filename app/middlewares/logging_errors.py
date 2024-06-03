from aiogram import Dispatcher
from aiogram.types import TelegramObject, Message, CallbackQuery, User
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from loguru import logger
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
            logger.error('Error occurred for user {0} ({1}): {2}'.format(user.id, user.username, e))
            raise e
        
