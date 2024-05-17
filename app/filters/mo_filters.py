from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

class MoPerformerFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        pass

class MoControlerFilter(BaseFilter):
    async def __call__(self, message: Message, session: AsyncSession) -> bool:
        pass