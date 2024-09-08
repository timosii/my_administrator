from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database.services.users import UserService


class MoPerformerFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_mo_performer(user_id=user_id)


class MoControlerFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_mo_controler(user_id=user_id)


class MoAvailFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_mo_avail(user_id=user_id)
