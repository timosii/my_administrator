import datetime as dt

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.database import session_maker
from app.database.repositories.check import CheckRepo
from app.database.schemas.check_schema import (
    CheckCreate,
    CheckInDB,
    CheckOut,
    CheckOutUnfinished,
    CheckTestCreate,
    CheckUpdate,
)
from app.handlers.messages import MfcMessages
from app.handlers.states import MfcStates
from app.keyboards.mfc_part import MfcKeyboards


class CheckService:
    def __init__(self, db_repository: CheckRepo = CheckRepo()):
        self.session_maker = session_maker
        self.db_repository = db_repository

    async def add_check(self, check_create: CheckCreate) -> CheckInDB:
        result = await self.db_repository.add_check(check_create=check_create)
        return result

    async def add_test_check(self, check_test_create: CheckTestCreate) -> CheckInDB:
        result = await self.db_repository.add_check(check_create=check_test_create)
        return result

    async def check_exists(self, check_id: int) -> bool:
        result = await self.db_repository.check_exists(check_id=check_id)
        return result

    async def get_check_by_id(self, check_id: int) -> CheckInDB:
        result = await self.db_repository.get_check_by_id(check_id=check_id)
        return result

    async def update_check(self, check_id: int, check_update: CheckUpdate) -> None:
        await self.db_repository.update_check(
            check_id=check_id, check_update=check_update
        )
        return

    async def delete_check(self, check_id: int) -> None:
        await self.db_repository.delete_check(check_id=check_id)
        return

    async def delete_all_checks(self) -> None:
        await self.db_repository.delete_all_checks()
        return

    async def get_all_checks(self) -> list[CheckInDB]:
        result = await self.db_repository.get_all_checks()
        return result

    async def get_all_active_checks_by_fil(
        self, fil_: str
    ) -> list[CheckInDB] | None:
        result = await self.db_repository.get_all_active_checks_by_fil(fil_=fil_)
        if not result:
            return None
        else:
            return result

    async def get_checks_count(self) -> int:
        result = await self.db_repository.get_all_checks()
        return result

    async def get_checks_by_mfc_user(self, user_id: int) -> list[CheckInDB]:
        result = await self.db_repository.get_checks_by_mfc_user(user_id=user_id)
        return result

    async def get_mfc_fil_active_checks(self, fil_: str) -> list[CheckInDB] | None:
        result = await self.db_repository.get_mfc_fil_active_checks(fil_=fil_)
        return result

    async def get_violations_found_count_by_check(self, check_id: int) -> int:
        result = await self.db_repository.get_violations_found_count_by_check(
            check_id=check_id
        )
        return result

    async def start_checking_process(
        self,
        message: Message,
        state: FSMContext,
        is_task: bool
    ):
        check_data = await state.get_data()
        check_obj = CheckCreate(
            fil_=check_data['fil_'],
            mfc_user_id=check_data['mfc_user_id'],
            is_task=is_task
        )
        check_in_obj = await self.add_check(check_create=check_obj)
        await message.answer(
            text=MfcMessages.choose_zone_with_time_task if is_task else MfcMessages.choose_zone_with_time,
            reply_markup=await MfcKeyboards().choose_zone(),
        )
        await state.update_data(
            check_in_obj.model_dump(mode='json')
        )
        await state.set_state(MfcStates.choose_zone)

    async def finish_check_process(
        self,
        check_id: int,
        state: FSMContext,
    ):
        current_time = dt.datetime.now(dt.timezone.utc)
        check_upd = CheckUpdate(mfc_finish=current_time)
        await self.update_check(check_id=check_id, check_update=check_upd)

    async def unfinished_checks_process(
        self,
        message: Message,
        state: FSMContext,
        checks: list[CheckInDB] | None,
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
                        f'check_unfinished_{check.check_id}': check.model_dump(mode='json'),
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
        check_obj = CheckInDB(**data[f'check_unfinished_{check_id}'])

        await state.update_data(
            check_obj.model_dump(mode='json')
        )
        await state.update_data({f'check_unfinished_{check_id}': None})
        await callback.answer(text='Продолжаем проверку')

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
