from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database.services.users import UserService


class MfcFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id

        return await UserService().is_mfc(user_id=user_id)


class MfcLeaderFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_mfc_leader(user_id=user_id)


class MfcAvailFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id
        return await UserService().is_mfc_avail(user_id=user_id)
