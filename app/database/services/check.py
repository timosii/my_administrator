import datetime as dt
from typing import Optional
from uuid import UUID

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.database import session_maker
from app.database.repositories.check import CheckRepo
from app.database.repositories.violations import ViolationsRepo
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

    async def check_exists(self, check_id: UUID) -> bool:
        result = await self.db_repository.check_exists(check_id=check_id)
        return result

    async def get_check_by_id(self, check_id: UUID) -> CheckInDB:
        result = await self.db_repository.get_check_by_id(check_id=check_id)
        return result

    async def update_check(self, check_id: str, check_update: CheckUpdate) -> None:
        check_id_ = UUID(check_id)
        await self.db_repository.update_check(
            check_id=check_id_, check_update=check_update
        )
        return

    async def delete_check(self, check_id: str) -> None:
        check_id_ = UUID(check_id)
        await self.db_repository.delete_check(check_id=check_id_)
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

    async def get_violations_found_count_by_check(self, check_id: str) -> int:
        check_id_ = UUID(check_id)
        result = await self.db_repository.get_violations_found_count_by_check(
            check_id=check_id_
        )
        return result

    async def get_violations_found_dict_ids_for_check(self, check_id: str) -> Optional[list[int]]:
        check_id_ = UUID(check_id)
        result = await self.db_repository.get_all_violations_found_dict_ids_for_check(
            check_id=check_id_
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
        check_id: str,
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
                    reply_markup=await MfcKeyboards().unfinished_check(check_id=check.check_id),
                )

    async def finish_unfinished_process(
        self,
        state: FSMContext,
        callback: CallbackQuery,
        check_id: str,
    ):
        data = await state.get_data()
        check_obj = CheckInDB(**data[f'check_unfinished_{check_id}'])

        await state.update_data(
            check_obj.model_dump(mode='json')
        )
        await state.update_data({f'check_unfinished_{check_id}': None})
        violation_dict_ids = await self.get_violations_found_dict_ids_for_check(check_id=check_id)
        if violation_dict_ids:
            vio_repo = ViolationsRepo()
            violations_completed: dict[str, dict] = {}
            for vio_dict_id in violation_dict_ids:
                violation = await vio_repo.get_violation_dict_by_id(violation_dict_id=vio_dict_id)
                zone = violation.zone
                violation_name = violation.violation_name
                problem = violation.problem
                zone_violations: dict = violations_completed.setdefault(zone, {})
                zone_violations.setdefault(violation_name, [])
                violations_completed[zone][violation_name].append(problem)
            await state.update_data({
                'violations_completed': violations_completed
            })
        await callback.answer(text='Продолжаем проверку')

    async def form_check_out(
        self,
        check: CheckInDB,
    ) -> CheckOut:
        check_id_ = str(check.check_id)
        check_out = CheckOut(
            check_id=check_id_,
            fil_=check.fil_,
            mfc_start=check.mfc_start,
            mfc_finish=check.mfc_finish,
            violations_count=await self.get_violations_found_count_by_check(
                check_id=check_id_
            ),
        )
        return check_out

    async def form_check_out_unfinished(
        self,
        check: CheckInDB,
    ) -> CheckOutUnfinished:
        check_id_ = str(check.check_id)
        check_out = CheckOutUnfinished(
            fil_=check.fil_,
            mfc_start=check.mfc_start,
            violations_count=await self.get_violations_found_count_by_check(
                check_id=check_id_
            ),
        )
        return check_out
