from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

class MfcFilter(BaseFilter):
    async def __call__(self, message: Message,
                       session: AsyncSession) -> bool:
        pass

class MfcAdminFIlter(BaseFilter):
    async def __call__(self, message: Message,
                       session: AsyncSession) -> bool:
        pass