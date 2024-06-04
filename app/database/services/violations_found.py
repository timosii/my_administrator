from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import CallbackQuery
from app.database.database import session_maker
from app.database.repositories.violations_found import ViolationFoundRepo
from app.database.repositories.violations import ViolationsRepo
from app.database.repositories.users import UserRepo
from app.database.models.data import ViolationFound
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundUpdate,
    ViolationFoundInDB,
    ViolationFoundOut,
)
from app.database.schemas.violation_schema import (
    ViolationInDB,
)
from app.database.schemas.user_schema import (
    UserInDB
)
from app.view.cards import FormCards
from loguru import logger


class ViolationFoundService:
    def __init__(self, db_repository: ViolationFoundRepo = ViolationFoundRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_violation(
        self, violation_create: ViolationFoundCreate
    ) -> ViolationFoundInDB:
        result = await self.db_repository.add_violation_found(
            violation_create=violation_create
        )
        return result

    async def violation_exists(self, violation_id: int) -> bool:
        result = await self.db_repository.violation_found_exists(
            violation_id=violation_id
        )
        return result

    async def get_violation_found_by_id(
        self, violation_id: int
    ) -> Optional[ViolationFoundInDB]:
        result = await self.db_repository.get_violation_found_by_id(
            violation_id=violation_id
        )
        return result

    async def update_violation(
        self, violation_id: int, violation_update: ViolationFoundUpdate
    ) -> None:
        result = await self.db_repository.update_violation_found(
            violation_id=violation_id, violation_update=violation_update
        )
        return result

    async def delete_violation(self, violation_id: int) -> None:
        result = await self.db_repository.delete_violation_found(
            violation_id=violation_id
        )
        return result

    async def get_all_violations(self) -> List[ViolationFoundInDB]:
        result = await self.db_repository.get_all_violations_found()
        return result

    async def get_violations_found_count_by_check(self, check_id: int) -> int:
        result = await self.db_repository.get_violations_found_count_by_check(
            check_id=check_id
        )
        return result

    async def get_violations_found_by_check(
        self, check_id: int
    ) -> List[ViolationFoundInDB]:
        result = await self.db_repository.get_violations_found_by_check(
            check_id=check_id
        )
        return result

    async def get_violations_found_by_fil(
        self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        result = await self.db_repository.get_violations_found_by_fil(fil_=fil_)
        if not result:
            return None
        return result

    async def get_id_by_name(self, violation_name: str, zone: str) -> int:
        result = await ViolationsRepo().get_id_by_name(
            zone=zone, violation_name=violation_name
        )
        return result

    async def get_violation_by_id(self, violation_id: int) -> Optional[ViolationInDB]:
        result = await ViolationsRepo().get_violation_by_id(violation_id=violation_id)
        return result if result else None
    
    async def is_violation_already_in_check(self, violation_dict_id: int, check_id: int) -> bool:
        result = await ViolationFoundRepo().is_violation_already_in_check(
            violation_dict_id=violation_dict_id,
            check_id=check_id
            )
        return result
    
    async def get_violation_performers_by_mo(
        self,
        mo: str
    ) -> Optional[List[UserInDB]]:
        performers = await UserRepo().get_user_performer_by_mo(mo=mo)
        return performers if performers else None
    
    async def get_description(self, violation_dict_id: int) -> Optional[str]:
        result = await ViolationsRepo().get_violation_by_id(
            violation_id=violation_dict_id,
            )
        return result.description if result else None
    
    async def send_vio_notification_to_mo_performers(self,
                                                 callback: CallbackQuery,
                                                 mo: str,
                                                 fil_: str,
                                                 violation: ViolationFoundInDB):
        performers = await self.get_violation_performers_by_mo(mo=mo)
        if performers:
            violation_found_out = await self.form_violation_out(violation=violation)
            res = await self.form_violation_card(violation=violation_found_out)
            for performer in performers:
                await callback.bot.send_message(performer.id, text=f"<b>Зарегистрировано новое нарушение в филиале {fil_}</b>\n{res}")
        else: 
            await callback.message.answer(text='Нет зарегистрированных исполнителей от МО')

    async def form_violation_out(
        self,
        violation: ViolationFoundInDB,
    ) -> ViolationFoundOut:
        vio = await self.get_violation_by_id(violation_id=violation.violation_id)
        vio_found = ViolationFoundOut(
            id=violation.id,
            violation_id=violation.violation_id,
            zone=vio.zone,
            violation_name=vio.violation_name,
            time_to_correct=vio.time_to_correct,
            violation_detected=violation.violation_detected,
            comm=violation.comm,
            photo_id=violation.photo_id,
        )
        return vio_found

    async def form_violation_card(
        self,
        violation: ViolationFoundOut,
    ) -> str:
        text_mes = FormCards().violation_card(violation=violation)
        return text_mes
    
