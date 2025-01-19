from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from app.database.repositories.cache_config import cache


class ThrottlingMiddleware(BaseMiddleware):
    ttl = .5

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get('event_from_user')
        throttling_key = await cache.get(f'throttling_{str(user.id)}')
        if throttling_key is not None:
            return
        else:
            await cache.set(f'throttling_{str(user.id)}', '+', ttl=self.ttl)
        return await handler(event, data)
