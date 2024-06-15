from pydantic import BaseModel
from aiogram.types import Message
from app.keyboards.mfc_part import MfcKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MfcMessages, DefaultMessages
from aiogram.fsm.context import FSMContext
from app.handlers.states import MfcStates
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.models.data import User
from app.database.schemas.user_schema import UserCreate, UserUpdate, UserInDB
from app.database.schemas.check_schema import CheckInDB
from app.database.repositories.users import UserRepo

class UserService:
    def __init__(self, db_repository: UserRepo = UserRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_user(self, user_create: UserCreate) -> UserInDB:
        result = await self.db_repository.add_user(user_create=user_create)
        return result
        
    # async def get_user_mo(self, user_id: int) -> str:
    #     result = await self.db_repository.get_user_mo(user_id=user_id)
    #     return result
    async def get_user_mo(self,
                          message: Message,
                          state: FSMContext) -> str:

        result = await self.db_repository.get_user_mo(user_id=user_id)
        return result

    async def user_exists(self, user_id: int) -> bool:
        result = await self.db_repository.user_exists(user_id=user_id)
        return result

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        result = await self.db_repository.get_user_by_id(user_id=user_id)
        return result

    async def update_user(self, user_id: int, user_update: UserUpdate) -> None:
        result = await self.db_repository.update_user(user_id=user_id, user_update=user_update)
        return result

    async def delete_user(self, user_id: int) -> None:
        result = await self.db_repository.delete_user(user_id=user_id)
        return result

    async def get_all_users(self) -> List[UserInDB]:
        result = await self.db_repository.get_all_users()
        return result
    
    async def delete_all_users(self) -> None:
        return await self.db_repository.delete_all_users()

    async def get_user_count(self) -> int:
        result = await self.db_repository.get_user_count()
        return result
    
    async def is_admin(self, user_id: int) -> bool:
        result = await self.db_repository.is_admin(user_id=user_id)
        return result       

    async def is_mfc(self, user_id: int) -> bool:
        result = await self.db_repository.is_mfc(user_id=user_id)
        return result  

    async def is_mfc_leader(self, user_id: int) -> bool:
        result = await self.db_repository.is_mfc_leader(user_id=user_id)
        return result  

    async def is_mo_performer(self, user_id: int) -> bool:
        result = await self.db_repository.is_mo_performer(user_id=user_id)
        return result  

    async def is_mo_controler(self, user_id: int) -> bool:
        result = await self.db_repository.is_mo_controler(user_id=user_id)
        return result  
