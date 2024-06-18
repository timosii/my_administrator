import datetime as dt
import time
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types import CallbackQuery, Message
from app.database.database import session_maker
from app.database.repositories.violations_found import ViolationFoundRepo
from app.database.repositories.violations import ViolationsRepo
from app.database.repositories.users import UserRepo
from aiogram.fsm.context import FSMContext
from app.database.models.data import ViolationFound
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundUpdate,
    ViolationFoundInDB,
    ViolationFoundOut,
)
from app.database.services.check import CheckService
from app.database.services.helpers import HelpService
from aiogram.exceptions import TelegramBadRequest
from app.database.schemas.check_schema import CheckUpdate
from app.handlers.messages import MfcMessages, MoPerformerMessages
from app.keyboards.mfc_part import MfcKeyboards
from app.keyboards.mo_part import MoPerformerKeyboards
from app.database.schemas.violation_schema import (
    ViolationInDB,
)
from app.database.schemas.user_schema import UserInDB
from app.view.cards import FormCards
from loguru import logger



# moscow_tz = pytz.timezone('Europe/Moscow')

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
        self, violation_found_id: int
    ) -> Optional[ViolationFoundInDB]:
        result = await self.db_repository.get_violation_found_by_id(
            violation_found_id=violation_found_id
        )
        return result
    
    async def get_violation_found_fil_by_id(
            self, violation_id: int
    ) -> str:
        return await self.db_repository.get_violation_found_fil_by_id(
            violation_id=violation_id
        )

    async def update_violation(
        self, violation_found_id: int, violation_update: ViolationFoundUpdate
    ) -> None:
        result = await self.db_repository.update_violation_found(
            violation_found_id=violation_found_id, violation_update=violation_update
        )
        return result

    async def delete_violation(self, violation_id: int) -> None:
        result = await self.db_repository.delete_violation_found(
            violation_id=violation_id
        )
        return result

    async def delete_all_violations_found(self) -> None:
        result = await self.db_repository.delete_all_violations_found()
        return result

    async def get_all_violations_found(self) -> List[ViolationFoundInDB]:
        result = await self.db_repository.get_all_violations_found()
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

    async def get_active_violations_by_fil(
        self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        result = await self.db_repository.get_active_violations_by_fil(fil_=fil_)
        if not result:
            return None
        return result
    
    async def get_pending_violations_by_fil(
        self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        result = await self.db_repository.get_pending_violations_by_fil(fil_=fil_)
        if not result:
            return None
        return result


    async def get_dict_id_by_name(self, violation_name: str, zone: str) -> int:
        result = await ViolationsRepo().get_dict_id_by_name(
            zone=zone, violation_name=violation_name
        )
        return result

    async def get_violation_dict_by_id(self, violation_dict_id: int) -> Optional[ViolationInDB]:
        result = await ViolationsRepo().get_violation_dict_by_id(violation_dict_id=violation_dict_id)
        return result if result else None

    async def is_violation_already_in_check(
        self, violation_dict_id: int, check_id: int
    ) -> bool:
        result = await ViolationFoundRepo().is_violation_already_in_check(
            violation_dict_id=violation_dict_id,
            check_id=check_id
        )
        return result
    
    async def is_violation_already_fixed(
        self, violation_found_id: int
    ) -> bool:
        result = await ViolationFoundRepo().is_violation_already_fixed(
            violation_found_id=violation_found_id
        )
        return result        

    async def get_violation_performers_by_fil(self, fil_: str) -> Optional[List[UserInDB]]:
        performers = await UserRepo().get_user_performer_by_fil(fil_=fil_)
        return performers if performers else None

    async def get_description(self, violation_dict_id: int) -> Optional[str]:
        result = await ViolationsRepo().get_violation_dict_by_id(
            violation_dict_id=violation_dict_id,
        )
        return result.description if result else None

    async def send_vio_notification_to_fil_performers(
        self, callback: CallbackQuery, violation: ViolationFoundOut
    ):
        performers = await self.get_violation_performers_by_fil(fil_=violation.fil_)
        if not performers:
            await callback.message.answer(
                text=MfcMessages.zero_performers
            )
            return
        else:
            res = violation.violation_card()
            await callback.message.answer(
                text=MfcMessages.send_to_mo(fil_=violation.fil_),
                reply_markup=ReplyKeyboardRemove()
                )    
            time.sleep(1)
            norm_users_count = 0
            troubles_user_count = 0
            for performer in performers:
                try:
                    if violation.photo_id_mfc:
                        await callback.bot.send_photo(
                            chat_id=performer.user_id,
                            photo=violation.photo_id_mfc,
                            caption=MfcMessages.there_is_new_violation(fil_=violation.fil_, text=res),
                            reply_markup=MfcKeyboards().take_task_to_work(
                                violation_id=violation.violation_found_id,
                                is_task=violation.is_task
                                )
                        )
                    else:
                        await callback.bot.send_message(
                            chat_id=performer.id,
                            text=MfcMessages.there_is_new_violation(fil_=violation.fil_, text=res),
                            reply_markup=MfcKeyboards().take_task_to_work(
                                violation_id=violation.violation_found_id,
                                is_task=violation.is_task
                            )
                        )
                    norm_users_count += 1
                except TelegramBadRequest:
                    troubles_user_count += 1
                    continue

            if norm_users_count > 0:   
                await callback.message.answer(
                    text=MfcMessages.violation_sending(fil_=violation.fil_, count=norm_users_count, flag=True),
                    reply_markup=ReplyKeyboardRemove()
                    )    
                
            if troubles_user_count > 0:    
                await callback.message.answer(
                    text=MfcMessages.violation_sending(fil_=violation.fil_, count=troubles_user_count, flag=False),
                    reply_markup=ReplyKeyboardRemove()
                )


    async def save_violation_process(
        self,
        callback: CallbackQuery,
        violation_found_out: ViolationFoundOut,
    ):
        await callback.message.edit_text(
            text=MfcMessages.save_violation(
                violation=violation_found_out.violation_name), reply_markup=None
        )

        vio_found_update = ViolationFoundUpdate(
            **violation_found_out.model_dump()
        )
        await self.update_violation(
            violation_found_id=violation_found_out.violation_found_id,
            violation_update=vio_found_update)

    async def form_task_replies(
        self,
        message: Message,
        state: FSMContext,
        fil_: str,
        tasks: Optional[List[ViolationFoundInDB]],
    ):
        if not tasks:
            await message.answer(
                text=MoPerformerMessages.form_no_tasks_answer(fil_=fil_),
            )
        else:
            for task in tasks:
                violation_out = await self.form_violation_out(violation=task)
                await state.update_data(
                    {f"vio_{violation_out.violation_found_id}": violation_out.model_dump(mode='json')}
                )
            data = await state.get_data()
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v and (v['is_task'] == True) and (v['is_pending'] == False))
                ],
                key=lambda x: x.violation_dict_id,
            )
            reply_obj = FormCards().form_reply(
                violations_out=violation_out_objects, order=0
            )
            photo_id = reply_obj.photo_id
            text_mes = reply_obj.text_mes
            keyboard = reply_obj.keyboard
            await message.answer_photo(
                photo=photo_id, caption=text_mes, reply_markup=keyboard
            )

    async def form_violations_replies(
        self,
        violations: List[ViolationFoundInDB],
        callback: CallbackQuery,
        state: FSMContext,
    ):
        if not violations:
            await callback.message.answer(
                text=MoPerformerMessages.no_violations,
                reply_markup=MoPerformerKeyboards().check_finished(),
            )
            await callback.answer()
        else:
            for violation in violations:
                violation_out = await self.form_violation_out(violation=violation)
                await state.update_data(
                    {f"vio_{violation_out.violation_found_id}": violation_out.model_dump(mode='json')}
                )

            data = await state.get_data()
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v and (v['is_task'] == False) and (v['is_pending'] == False))
                ],
                key=lambda x: x.violation_dict_id,
            )

            reply_obj = FormCards().form_reply(
                violations_out=violation_out_objects, order=0
            )
            photo_id = reply_obj.photo_id
            text_mes = reply_obj.text_mes
            keyboard = reply_obj.keyboard
            if photo_id:
                await callback.message.answer_photo(
                    photo=photo_id, caption=text_mes, reply_markup=keyboard
                )
            else:
                await callback.message.answer(
                    text=text_mes, reply_markup=keyboard
                )

            await callback.answer()

    async def form_violations_pending_replies(
        self,
        message: Message,
        state: FSMContext,
        fil_: str,
        violations_pending: Optional[List[ViolationFoundInDB]],
    ):
        if not violations_pending:
            await message.answer(
                text=MoPerformerMessages.form_no_pending_violations_answer(fil_=fil_),
            )
        else:
            for violation_found in violations_pending:
                violation_out = await self.form_violation_out(violation=violation_found)
                await state.update_data(
                    {f"vio_{violation_out.violation_found_id}": violation_out.model_dump(mode='json')}
                )
            data = await state.get_data()
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**v)
                    for k, v in data.items()
                    if (k.startswith("vio_") and v and (v['is_pending'] == True))
                ],
                key=lambda x: x.violation_dict_id,
            )
            reply_obj = FormCards().form_violation_pending_reply(
                violations_out=violation_out_objects, order=0
            )
            photo_id = reply_obj.photo_id
            text_mes = reply_obj.text_mes
            keyboard = reply_obj.keyboard
            await message.answer_photo(
                photo=photo_id, caption=text_mes, reply_markup=keyboard
            )

    async def form_violation_out(
        self,
        violation: ViolationFoundInDB,
        check_obj: CheckService = CheckService(),
        help_obj: HelpService=HelpService()
    ) -> ViolationFoundOut:
        check = await check_obj.get_check_by_id(check_id=violation.check_id)
        vio = await self.get_violation_dict_by_id(violation_dict_id=violation.violation_dict_id)
        mo = await help_obj.get_mo_by_fil(fil_=check.fil_)
        vio_found = ViolationFoundOut(
            mo=mo,
            fil_=check.fil_,
            is_task=check.is_task,
            check_id=violation.check_id,
            violation_found_id=violation.violation_found_id,
            violation_dict_id=violation.violation_dict_id,
            zone=vio.zone,
            violation_name=vio.violation_name,
            time_to_correct=vio.time_to_correct,
            violation_detected=violation.violation_detected,
            comm_mfc=violation.comm_mfc,
            photo_id_mfc=violation.photo_id_mfc,
            is_pending=violation.is_pending,
            violation_pending=violation.violation_pending
        )
        return vio_found  

    # async def form_violation_card(
    #     self,
    #     violation: ViolationFoundOut,
    # ) -> str:
    #     text_mes = FormCards().violation_card(violation=violation)
    #     return text_mes
