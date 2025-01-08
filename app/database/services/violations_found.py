import asyncio
from typing import Optional
from uuid import UUID

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.media_group import MediaGroupBuilder

from app.config import settings
from app.database.database import session_maker
from app.database.repositories.cache_config import cached
from app.database.repositories.users import UserRepo
from app.database.repositories.violations import ViolationsRepo
from app.database.repositories.violations_found import ViolationFoundRepo
from app.database.schemas.user_schema import UserInDB
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundInDB,
    ViolationFoundOut,
    ViolationFoundTestCreate,
    ViolationFoundUpdate,
)
from app.database.schemas.violation_schema import ViolationInDB
from app.database.services.check import CheckService
from app.database.services.helpers import HelpService
from app.handlers.messages import MfcMessages, MoPerformerMessages
from app.handlers.user.mo_part.performer_card_constructor import MoPerformerCard
from app.keyboards.mfc_part import MfcKeyboards
from app.keyboards.mo_part import MoPerformerKeyboards

CACHE_EXPIRE_SHORT = settings.CACHE_SHORT
CACHE_EXPIRE_LONG = settings.CACHE_LONG


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

    async def add_test_violation(
        self, violation_test_create: ViolationFoundTestCreate
    ) -> ViolationFoundInDB:
        result = await self.db_repository.add_violation_found(
            violation_create=violation_test_create
        )
        return result

    async def violation_exists(self, violation_id: int) -> bool:
        result = await self.db_repository.violation_found_exists(
            violation_id=violation_id
        )
        return result

    async def get_violation_found_by_id(
        self, violation_found_id: str
    ) -> ViolationFoundInDB | None:
        violation_found_id_ = UUID(violation_found_id)
        result = await self.db_repository.get_violation_found_by_id(
            violation_found_id=violation_found_id_
        )
        return result

    async def get_violation_found_fil_by_id(
            self, violation_id: str
    ) -> Optional[str]:
        return await self.db_repository.get_violation_found_fil_by_id(
            violation_id=violation_id
        )

    async def update_violation(
        self, violation_found_id: str, violation_update: ViolationFoundUpdate
    ) -> None:
        violation_found_id_ = UUID(violation_found_id)
        await self.db_repository.update_violation_found(
            violation_found_id=violation_found_id_, violation_update=violation_update
        )
        return

    async def delete_violation(self, violation_id: UUID) -> None:
        await self.db_repository.delete_violation_found(
            violation_id=violation_id
        )
        return

    async def delete_all_violations_found(self) -> None:
        await self.db_repository.delete_all_violations_found()
        return

    async def get_all_violations_found(self) -> list[ViolationFoundInDB]:
        result = await self.db_repository.get_all_violations_found()
        return result

    async def get_violations_found_by_check(
        self, check_id: int
    ) -> Optional[list[ViolationFoundInDB]]:
        result = await self.db_repository.get_violations_found_by_check(
            check_id=check_id
        )
        return result

    async def get_violations_found_by_fil(
        self, fil_: str
    ) -> list[ViolationFoundInDB] | None:
        result = await self.db_repository.get_violations_found_by_fil(fil_=fil_)
        if not result:
            return None
        return result

    async def user_empty_violations_found_process(
            self, user_id: int
    ) -> None:
        result = await self.db_repository.get_user_empty_violations(
            user_id=user_id
        )
        if not result:
            return None
        else:
            for violation in result:
                await self.delete_violation(violation_id=violation.violation_found_id)

    async def get_active_violations_by_fil(
        self, fil_: str
    ) -> list[ViolationFoundInDB] | None:
        result = await self.db_repository.get_active_violations_by_fil(fil_=fil_)
        if not result:
            return None
        return result

    async def get_pending_violations_by_fil(
        self, fil_: str
    ) -> list[ViolationFoundInDB] | None:
        result = await self.db_repository.get_pending_violations_by_fil(fil_=fil_)
        if not result:
            return None
        return result

    async def get_dict_id_by_name(self, violation_name: str, zone: str, problem: str) -> int:
        result = await ViolationsRepo().get_dict_id_by_name(
            zone=zone, violation_name=violation_name, problem=problem
        )
        return result

    async def get_violation_dict_by_id(self, violation_dict_id: int) -> ViolationInDB:
        result = await ViolationsRepo().get_violation_dict_by_id(violation_dict_id=violation_dict_id)
        return result

    async def is_violation_already_in_check(
        self, violation_dict_id: int, check_id: UUID
    ) -> bool:
        result = await ViolationFoundRepo().is_violation_already_in_check(
            violation_dict_id=violation_dict_id,
            check_id=check_id
        )
        return result

    async def is_violation_already_fixed(
        self, violation_found_id: str
    ) -> bool:
        violation_found_id_ = UUID(violation_found_id)
        result = await ViolationFoundRepo().is_violation_already_fixed(
            violation_found_id=violation_found_id_
        )
        return result

    async def is_violation_already_pending(
        self, violation_found_id: UUID
    ) -> bool:
        result = await ViolationFoundRepo().is_violation_already_pending(
            violation_found_id=violation_found_id
        )
        return result

    async def get_pending_violations_by_fil_n_dict_id(
        self,
        fil_: str,
        violation_dict_id: int
    ) -> list[ViolationFoundInDB] | None:
        result = await ViolationFoundRepo().get_pending_violations_by_fil_n_dict_id(
            fil_=fil_,
            violation_dict_id=violation_dict_id
        )
        return result

    async def get_violation_performers_by_fil(self, fil_: str) -> list[UserInDB] | None:
        performers = await UserRepo().get_user_performer_by_fil(fil_=fil_)
        return performers if performers else None

    async def get_description(self, violation_dict_id: int) -> str | None:
        result = await ViolationsRepo().get_violation_dict_by_id(
            violation_dict_id=violation_dict_id,
        )
        return result.description if result else None

    async def send_vio_notification_to_fil_performers(
        self,
        callback: CallbackQuery,
        violation: ViolationFoundOut
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
                text=await MfcMessages.send_to_mo(fil_=violation.fil_),
                reply_markup=ReplyKeyboardRemove()
            )
            await callback.message.answer_sticker(
                sticker=MoPerformerMessages.send_sticker
            )
            await asyncio.sleep(1)
            norm_users_count = 0
            troubles_user_count = 0
            for performer in performers:
                try:
                    if violation.photo_id_mfc:
                        await callback.bot.send_photo(
                            chat_id=performer.user_id,
                            photo=violation.photo_id_mfc[0],
                            caption=await MfcMessages.there_is_new_violation(fil_=violation.fil_, text=res),
                            reply_markup=await MfcKeyboards().take_task_to_work(
                                violation_id=violation.violation_found_id,
                                is_task=violation.is_task
                            )
                        )
                    else:
                        await callback.bot.send_message(
                            chat_id=performer.id,
                            text=await MfcMessages.there_is_new_violation(fil_=violation.fil_, text=res),
                            reply_markup=await MfcKeyboards().take_task_to_work(
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
                    text=await MfcMessages.violation_sending(fil_=violation.fil_, count=norm_users_count, flag=True),
                    reply_markup=ReplyKeyboardRemove()
                )

            if troubles_user_count > 0:
                await callback.message.answer(
                    text=await MfcMessages.violation_sending(fil_=violation.fil_, count=troubles_user_count, flag=False),
                    reply_markup=ReplyKeyboardRemove()
                )

    async def save_violation_process(
        self,
        callback: CallbackQuery,
        violation_found_out: ViolationFoundOut,
    ):
        await callback.message.edit_text(
            text=await MfcMessages.save_violation(
                zone=violation_found_out.zone,
                violation_name=violation_found_out.violation_name,
                problem=violation_found_out.problem
            ), reply_markup=None
        )

        vio_found_update = ViolationFoundUpdate(
            **violation_found_out.model_dump()
        )
        await self.update_violation(
            violation_found_id=violation_found_out.violation_found_id,
            violation_update=vio_found_update)

    async def update_data_violations_found_active(
        self,
        state: FSMContext,
        data: dict,
        message: Message | None = None,
        callback: CallbackQuery | None = None,
    ) -> None:
        fil_ = data['fil_']
        mo_user_id = data['mo_user_id']
        violations_found_active = await self.get_active_violations_by_fil(fil_=fil_)
        if not violations_found_active:
            if callback:
                await callback.message.answer_sticker(
                    sticker=MoPerformerMessages.find_sticker,
                    reply_markup=await MoPerformerKeyboards().check_or_tasks(),
                )
                await asyncio.sleep(1)
            if message:
                await message.answer_sticker(
                    sticker=MoPerformerMessages.find_sticker,
                    reply_markup=await MoPerformerKeyboards().check_or_tasks(),
                )
                await asyncio.sleep(1)
        else:
            for violation_found in violations_found_active:
                violation_out = await self.form_violation_out(mo_user_id=mo_user_id, violation=violation_found)
                await state.update_data(
                    {f'vio_{violation_out.violation_found_id}': violation_out.model_dump(mode='json')}
                )

    async def update_data_violations_found_in_check(
        self,
        callback: CallbackQuery,
        state: FSMContext,
        data: dict,
    ):
        check_id = data['check_id']
        mo_user_id = data['mo_user_id']
        violations_found_check = await self.get_violations_found_by_check(check_id=check_id)
        if not violations_found_check:
            await callback.message.answer_sticker(
                sticker=MoPerformerMessages.find_sticker,
                reply_markup=await MoPerformerKeyboards().check_finished(),
            )
            await asyncio.sleep(1)
        else:
            for violation_found in violations_found_check:
                violation_out = await self.form_violation_out(mo_user_id=mo_user_id, violation=violation_found)
                await state.update_data(
                    {f'vio_{violation_out.violation_found_id}': violation_out.model_dump(mode='json')}
                )

    async def update_data_violations_found_pending(
        self,
        message: Message,
        state: FSMContext,
        data: dict,
    ) -> None:
        mo_user_id = data['mo_user_id']
        violations_found_pending = await self.get_pending_violations_by_fil(fil_=data['fil_'])
        if not violations_found_pending:
            await message.answer_sticker(
                sticker=MoPerformerMessages.find_sticker,
            )
            await asyncio.sleep(1)
            violations_found_out_pending_data = await MoPerformerCard(data=data).get_pending_violations()
            await state.update_data(
                {f'vio_{violation_out.violation_found_id}': None for violation_out in violations_found_out_pending_data}
            )
        else:
            for violation_found in violations_found_pending:
                violation_out = await self.form_violation_out(mo_user_id=mo_user_id, violation=violation_found)
                await state.update_data(
                    {f'vio_{violation_out.violation_found_id}': violation_out.model_dump(mode='json')}
                )

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='violation_found')
    async def form_violation_out(
        self,
        violation: ViolationFoundInDB,
        mo_user_id: int | None = None,
        check_obj: CheckService = CheckService(),
        help_obj: HelpService = HelpService()
    ) -> ViolationFoundOut:
        check = await check_obj.get_check_by_id(check_id=violation.check_id)
        vio = await self.get_violation_dict_by_id(violation_dict_id=violation.violation_dict_id)
        mo = await help_obj.get_mo_by_fil(fil_=check.fil_)
        vio_found = ViolationFoundOut(
            mo=mo,
            fil_=check.fil_,
            mo_user_id=mo_user_id,
            is_task=check.is_task,
            check_id=str(violation.check_id),
            violation_found_id=str(violation.violation_found_id),
            violation_dict_id=violation.violation_dict_id,
            zone=vio.zone,
            violation_name=vio.violation_name,
            problem=vio.problem,
            time_to_correct=vio.time_to_correct,
            violation_detected=violation.violation_detected,
            comm_mfc=violation.comm_mfc,
            photo_id_mfc=violation.photo_id_mfc,
            comm_mo=violation.comm_mo,
            is_pending=violation.is_pending,
            violation_pending=violation.violation_pending,
            pending_period=violation.pending_period
        )
        return vio_found

    @cached(ttl=CACHE_EXPIRE_SHORT, namespace='violation_found')
    async def get_all_photos(
        callback: CallbackQuery,
        violation_found_obj: ViolationFoundOut
    ):
        photo_ids = violation_found_obj.photo_id_mfc

        if not photo_ids:
            await callback.answer(text='Фотографий нет')
            return

        if len(photo_ids) < 2:
            await callback.answer(text='Больше фотографий нет')
            return

        if len(photo_ids) > 10:
            photo_ids = photo_ids[:10]

        violation_name = violation_found_obj.violation_name
        media_group = MediaGroupBuilder(caption=violation_name)
        for photo_id in photo_ids:
            media_group.add_photo(media=photo_id)
        await callback.message.answer_media_group(
            media=media_group.build(),
        )
        await callback.answer()
