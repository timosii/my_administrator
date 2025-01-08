from aiogram.fsm.context import FSMContext

from app.database.schemas.helpers import Reply
from app.database.schemas.violation_found_schema import (
    ViolationFoundInDB,
    ViolationFoundOut,
)
from app.database.services.violations_found import ViolationFoundService
from app.keyboards.mfc_part import MfcKeyboards


class MfcPendingCard:
    def __init__(self
                 ) -> None:
        pass

    async def get_violations_out_lst(self,
                                     pending_violations_in: list[ViolationFoundInDB],
                                     violation_obj: ViolationFoundService = ViolationFoundService()):
        self.violations_found_out = [
            await violation_obj.form_violation_out(violation=vio) for vio in pending_violations_in
        ]

    async def save_to_data(self,
                           state: FSMContext):
        await state.update_data(
            {
                f'vio_{vio.violation_found_id}': vio.model_dump(mode='json') for vio in self.violations_found_out
            }
        )

    async def save_to_data_process(self,
                                   state: FSMContext,
                                   pending_violations_in: list[ViolationFoundInDB]
                                   ):
        await self.get_violations_out_lst(pending_violations_in=pending_violations_in)
        await self.save_to_data(state=state)

    async def get_violations_out_from_data(self,
                                           state: FSMContext) -> list[ViolationFoundOut]:
        data = await state.get_data()
        violations_out_from_data = [
            ViolationFoundOut(**v)
            for k, v in data.items()
            if (k.startswith('vio_') and v)
        ]
        violations_out_from_data = sorted(
            violations_out_from_data,
            key=lambda x: x.violation_pending if x.violation_pending else x,
        )
        return violations_out_from_data

    async def form_reply(self,
                         violations_out: list[ViolationFoundOut],
                         order: int = 0,
                         ) -> Reply:
        photo_id = violations_out[order].photo_id_mfc[0] if violations_out[order].photo_id_mfc else None  # type: ignore
        text_mes = violations_out[order].violation_card_pending()
        prev_order = order - 1
        next_order = order + 1
        keyboard = MfcKeyboards().get_violation_pending_menu(
            prev_violation_id=violations_out[prev_order].violation_found_id,
            violation_id=violations_out[order].violation_found_id,
            next_violation_id=(
                violations_out[next_order].violation_found_id
                if order != (len(violations_out) - 1)
                else violations_out[0].violation_found_id
            ),
        )
        return Reply(
            photo=photo_id,
            caption=text_mes,
            reply_markup=keyboard
        )

    async def _get_index_violation_found(self,
                                         state: FSMContext,
                                         violation_found_id: str) -> int:
        violations_out_from_data = await self.get_violations_out_from_data(state=state)
        for index, obj in enumerate(violations_out_from_data):
            if obj.violation_found_id == violation_found_id:
                return index
        return 0

    async def get_next_prev_reply(self,
                                  state: FSMContext,
                                  violation_found_out: ViolationFoundOut,
                                  ):
        violations_out_from_data = await self.get_violations_out_from_data(state=state)
        if len(violations_out_from_data) == 1:
            return None

        order = await self._get_index_violation_found(
            state=state,
            violation_found_id=violation_found_out.violation_found_id
        )
        reply_obj = await self.form_reply(
            violations_out=violations_out_from_data,
            order=order,
        )

        return reply_obj
