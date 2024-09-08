from dataclasses import dataclass
from typing import Optional

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.database import session_maker
from app.database.repositories.users import UserRepo
from app.database.schemas.user_schema import UserCreate, UserInDB, UserUpdate


@dataclass
class Name:
    last_name: str
    first_name: str
    patronymic: str | None = None

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

    async def get_name(self, user_id: int) -> Optional[str]:
        user = await self.get_user_by_id(user_id=user_id)
        if not user:
            return None
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

    async def get_user_by_id(self, user_id: int) -> UserInDB | None:
        result = await self.db_repository.get_user_by_id(user_id=user_id)
        return result

    async def update_user(self, user_id: int, user_update: UserUpdate) -> None:
        await self.db_repository.update_user(user_id=user_id, user_update=user_update)
        return

    async def delete_user(self, user_id: int) -> None:
        await self.db_repository.delete_user(user_id=user_id)
        return

    async def get_all_users(self) -> list[UserInDB]:
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

    async def is_mfc_avail(self, user_id: int) -> bool:
        result = await self.db_repository.is_mfc_avail(user_id=user_id)
        return result

    async def is_mo_avail(self, user_id: int) -> bool:
        result = await self.db_repository.is_mo_avail(user_id=user_id)
        return result

    async def is_mo_performer(self, user_id: int) -> bool:
        result = await self.db_repository.is_mo_performer(user_id=user_id)
        return result

    async def is_mo_controler(self, user_id: int) -> bool:
        result = await self.db_repository.is_mo_controler(user_id=user_id)
        return result

    async def get_avail_performer_by_fil(self, fil_: str) -> Optional[list[UserInDB]]:
        performers = await self.db_repository.get_avail_performer_by_fil(fil_=fil_)
        return performers if performers else None

    async def save_default_user_info(
            self,
            state: FSMContext,
            event: Message | CallbackQuery
    ):
        user = event.from_user
        mo = await self.get_user_mo(user_id=user.id)
        fil_ = await self.get_user_fil(user_id=user.id)
        await state.update_data(mo_user_id=user.id,
                                mo=mo,
                                fil_=fil_
                                )
