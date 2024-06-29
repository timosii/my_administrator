from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database.services.users import UserService


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_admin(user_id=user_id)
