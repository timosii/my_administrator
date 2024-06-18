from pydantic import BaseModel
from aiogram.types import Message, CallbackQuery
from app.keyboards.mfc_part import MfcKeyboards
from app.keyboards.default import DefaultKeyboards
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
from dataclasses import dataclass


@dataclass
class Name:
    last_name: str
    first_name: str
    patronymic: Optional[str] = None

    def get_greeting_name(self):
        if self.patronymic:
            return f'{self.first_name} {self.patronymic}'
        else:
            return f'{self.first_name}'


class UserService:
    def __init__(self, db_repository: UserRepo = UserRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_user(self, user_create: UserCreate) -> UserInDB:
        result = await self.db_repository.add_user(user_create=user_create)
        return result
        
    async def get_name(self, user_id: int) -> str:
        user = await self.get_user_by_id(user_id=user_id)
        name = Name(
            last_name=user.last_name,
            first_name=user.first_name,
            patronymic=user.patronymic,
        )
        return name.get_greeting_name()

    async def get_user_mo(self, user_id: int) -> str:
        result = await self.db_repository.get_user_mo(user_id=user_id)
        return result

    async def get_user_fil(self, user_id: int) -> str:
        result = await self.db_repository.get_user_fil(user_id=user_id)
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
    
    async def save_default_user_info(
            self,
            state: FSMContext,
            message: Message=None,
            callback: CallbackQuery=None
    ):
        if callback:
            user = callback.from_user
        else:
            user = message.from_user

        mo = await self.get_user_mo(user_id=user.id)
        fil_ = await self.get_user_fil(user_id=user.id)
        await state.update_data(mo_user_id=user.id,
                                mo=mo,
                                fil_=fil_
                                )
                
