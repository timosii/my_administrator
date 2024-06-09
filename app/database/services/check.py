import json
from loguru import logger
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import session_maker
from app.database.repositories.check import CheckRepo
from app.database.models.data import Check
from app.database.schemas.check_schema import (
    CheckCreate,
    CheckUpdate,
    CheckInDB,
    CheckOut,
    CheckOutUnfinished,
)
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# from app.database.services.check import CheckService
from app.view.cards import FormCards
from app.keyboards.mfc_part import MfcKeyboards
from app.handlers.messages import MfcMessages


class CheckService:
    def __init__(self, db_repository: CheckRepo = CheckRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_check(self, check_create: CheckCreate) -> CheckInDB:
        result = await self.db_repository.add_check(check_create=check_create)
        return result

    async def check_exists(self, check_id: int) -> bool:
        result = await self.db_repository.check_exists(check_id=check_id)
        return result

    async def get_check_by_id(self, check_id: int) -> Optional[CheckInDB]:
        result = await self.db_repository.get_check_by_id(check_id=check_id)
        return result

    async def update_check(self, check_id: int, check_update: CheckUpdate) -> None:
        result = await self.db_repository.update_check(
            check_id=check_id, check_update=check_update
        )
        return result

    async def delete_check(self, check_id: int) -> None:
        result = await self.db_repository.delete_check(check_id=check_id)
        return result

    async def delete_all_checks(self) -> None:
        result = await self.db_repository.delete_all_checks()
        return result

    async def get_all_checks(self) -> List[CheckInDB]:
        result = await self.db_repository.get_all_checks()
        return result

    async def get_all_active_checks_by_fil(
        self, fil_: str
    ) -> Optional[List[CheckInDB]]:
        result = await self.db_repository.get_all_active_checks_by_fil(fil_=fil_)
        if not result:
            return None
        else:
            return result

    async def get_checks_count(self) -> int:
        result = await self.db_repository.get_all_checks()
        return result

    async def get_checks_by_mfc_user(self, user_id: int) -> List[CheckInDB]:
        result = await self.db_repository.get_checks_by_mfc_user(user_id=user_id)
        return result
    
    async def get_mfc_fil_active_checks(self, fil_: str) -> Optional[List[CheckInDB]]:
        result = await self.db_repository.get_mfc_fil_active_checks(fil_=fil_)
        return result
    
    async def get_violations_found_count_by_check(self, check_id: int) -> int:
        result = await self.db_repository.get_violations_found_count_by_check(
            check_id=check_id
        )
        return result

    async def unfinished_checks_process(
        self,
        message: Message,
        state: FSMContext,
        checks: Optional[List[CheckInDB]],
    ):
        if not checks:
            await message.answer(
                text=MfcMessages.no_unfinished, reply_markup=message.reply_markup
            )
        else:
            for check in checks:
                check_out = await self.form_check_out_unfinished(check=check)
                text_mes = check_out.form_card_unfinished_out()
                await state.update_data(
                    {
                        f"check_unfinished_{check.check_id}": check.model_dump(mode='json'),
                    }
                )
                await message.answer(
                    text=text_mes,
                    reply_markup=MfcKeyboards().unfinished_check(check_id=check.check_id),
                )

    async def finish_unfinished_process(
        self,
        state: FSMContext,
        callback: CallbackQuery,
        check_id: int,
    ):
        data = await state.get_data()
        check_obj = CheckInDB(**data[f"check_unfinished_{check_id}"])

        await state.update_data( 
            check_obj.model_dump(mode='json')
        )
        await state.update_data({f"check_unfinished_{check_id}": None})
        await callback.answer(text="Продолжаем проверку")

    async def form_check_out(
        self,
        check: CheckInDB,
    ) -> CheckOut:
        check_out = CheckOut(
            check_id=check.check_id,
            fil_=check.fil_,
            mfc_start=check.mfc_start,
            mfc_finish=check.mfc_finish,
            violations_count=await self.get_violations_found_count_by_check(
                check_id=check.check_id
            ),
        )
        return check_out

    async def form_check_out_unfinished(
        self,
        check: CheckInDB,
        # check_obj: CheckService=CheckService()
    ) -> CheckOutUnfinished:
        check_out = CheckOutUnfinished(
            fil_=check.fil_,
            mfc_start=check.mfc_start,
            violations_count=await self.get_violations_found_count_by_check(
                check_id=check.check_id
            ),
        )
        return check_out

    # async def form_check_card(
    #     self,
    #     check: CheckOut,
    # ) -> str:
    #     text_mes = FormCards().check_card(check=check)
    #     return text_mes

    # async def form_check_card_unfinished(
    #     self,
    #     check: CheckOutUnfinished,
    # ) -> str:
    #     text_mes = check.form_card_out()
    #     return text_mes
