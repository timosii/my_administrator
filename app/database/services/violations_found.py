import datetime as dt
import json
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
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
    
    async def get_violation_found_fil_by_id(
            self, violation_id: int
    ) -> str:
        return await self.db_repository.get_violation_found_fil_by_id(
            violation_id=violation_id
        )

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

    async def delete_all_violations_found(self) -> None:
        result = await self.db_repository.delete_all_violations_found()
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

    async def get_active_violations_by_fil(
        self, fil_: str
    ) -> Optional[List[ViolationFoundInDB]]:
        result = await self.db_repository.get_active_violations_by_fil(fil_=fil_)
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

    async def is_violation_already_in_check(
        self, violation_dict_id: int, check_id: int
    ) -> bool:
        result = await ViolationFoundRepo().is_violation_already_in_check(
            violation_dict_id=violation_dict_id, check_id=check_id
        )
        return result

    async def get_violation_performers_by_mo(self, mo: str) -> Optional[List[UserInDB]]:
        performers = await UserRepo().get_user_performer_by_mo(mo=mo)
        return performers if performers else None

    async def get_description(self, violation_dict_id: int) -> Optional[str]:
        result = await ViolationsRepo().get_violation_by_id(
            violation_id=violation_dict_id,
        )
        return result.description if result else None

    async def send_vio_notification_to_mo_performers(
        self, callback: CallbackQuery, mo: str, fil_: str, violation: ViolationFoundInDB, is_task: bool
    ):
        performers = await self.get_violation_performers_by_mo(mo=mo)
        if performers:
            violation_found_out = await self.form_violation_out(violation=violation)
            res = await self.form_violation_card(violation=violation_found_out)
            await callback.message.answer(
                text=f"Оповещение о нарушении отправлено сотрудникам {mo}"
            )
            for performer in performers:
                if violation.photo_id:
                    await callback.bot.send_photo(
                        chat_id=performer.id,
                        photo=violation.photo_id,
                        caption=f"<b>Зарегистрировано новое нарушение в филиале {fil_}</b>\n{res}",
                        reply_markup=MfcKeyboards().take_task_to_work(
                            violation_id=violation.id,
                            is_task=1 if is_task else 0
                            )
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=performer.id,
                        text=f"<b>Зарегистрировано новое нарушение в филиале {fil_}</b>\n{res}",
                        reply_markup=MfcKeyboards().take_task_to_work(
                            violation_id=violation.id,
                            is_task=1 if is_task else 0
                        )
                    )
        else:
            await callback.message.answer(
                text="Отправка уведомления в МО невозможна: нет зарегистрированных исполнителей от МО"
            )

    async def save_violation_process(
        self,
        callback: CallbackQuery,
        vio_data: dict,
    ):
        violation_name = vio_data["violation_name"]
        await callback.message.edit_text(
            text=MfcMessages.save_violation(violation=violation_name), reply_markup=None
        )

        vio_obj = ViolationFoundCreate(
            check_id=vio_data["check_id"],
            violation_id=vio_data["violation_dict_id"],
            photo_id=vio_data["photo_id"],
            comm=vio_data["comm"],
        )
        vio_in_db = await self.add_violation(violation_create=vio_obj)
        logger.info(f'IS_TASK_IS: {bool(vio_data.get("is_task"))}')
        await self.send_vio_notification_to_mo_performers(
            callback=callback,
            mo=vio_data["mo"],
            fil_=vio_data["fil_"],
            violation=vio_in_db,
            is_task=bool(vio_data.get('is_task'))
        )

    async def form_task_replies(
        self,
        message: Message,
        state: FSMContext,
        fil_: str,
        mo_start: str | None,
        tasks: Optional[List[ViolationFoundInDB]],
    ):
        if not tasks:
            await message.answer(
                text=MoPerformerMessages.form_no_tasks_answer(fil_=fil_),
                reply_markup=message.reply_markup,
            )
        else:
            await state.update_data(fil_=fil_, mo_user_id=message.from_user.id)
            if not mo_start:
                await state.update_data(mo_start=dt.datetime.now().isoformat())
            for task in tasks:
                violation_out = await self.form_violation_out(violation=task)
                await state.update_data(
                    {f"vio_{violation_out.id}": violation_out.model_dump_json()}
                )
            data = await state.get_data()
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**json.loads(v))
                    for k, v in data.items()
                    if (k.startswith("vio_") and v)
                ],
                key=lambda x: x.violation_id,
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
                    {f"vio_{violation_out.id}": violation_out.model_dump_json()}
                )

            data = await state.get_data()
            violation_out_objects = sorted(
                [
                    ViolationFoundOut(**json.loads(v))
                    for k, v in data.items()
                    if (k.startswith("vio_") and v)
                ],
                key=lambda x: x.violation_id,
            )

            reply_obj = FormCards().form_reply(
                violations_out=violation_out_objects, order=0
            )
            photo_id = reply_obj.photo_id
            text_mes = reply_obj.text_mes
            keyboard = reply_obj.keyboard
            await callback.message.answer_photo(
                photo=photo_id, caption=text_mes, reply_markup=keyboard
            )
            await callback.answer()

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
