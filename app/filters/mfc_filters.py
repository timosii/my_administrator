from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.methods.users import is_mfc_leader, is_mfc

class MfcFilter(BaseFilter):
    async def __call__(self, message: Message)-> bool:
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        return await is_mfc(id=user_id)
        

class MfcLeaderFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        
        user_id = message.from_user.id
        return await is_mfc_leader(id=user_id)