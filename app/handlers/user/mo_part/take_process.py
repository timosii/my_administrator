import datetime as dt
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.keyboards.mo_part import MoPerformerKeyboards
from app.handlers.messages import MoPerformerMessages
from app.handlers.states import MoPerformerStates
from app.filters.mo_filters import MoPerformerFilter
from app.database.services.violations_found import ViolationFoundService
from app.database.services.users import UserService


router = Router()
router.message.filter(MoPerformerFilter())


@router.callback_query(
    F.data.startswith("take_"), 
    ~StateFilter(MoPerformerStates.correct_violation)
)
async def take_to_work(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService=ViolationFoundService(),
    user_obj: UserService=UserService()
):
    await state.clear()
    await user_obj.save_default_user_info(
        event=callback,
        state=state,
    )
    violation_found_id = int(callback.data.split("_")[1])
    is_fixed = await violation_obj.is_violation_already_fixed(
        violation_found_id=violation_found_id
    )
    if is_fixed:
        await callback.answer(text=MoPerformerMessages.violation_already_fixed)
        await callback.message.delete()
        return

    violation_in_db = await violation_obj.get_violation_found_by_id(
        violation_found_id=violation_found_id
    )
    data = await state.get_data()
    mo_user_id = data['mo_user_id']
    violation_out = await violation_obj.form_violation_out(
        mo_user_id=mo_user_id,
        violation=violation_in_db)
    current_time = dt.datetime.now(dt.timezone.utc)
    if violation_out.is_task:
        await state.update_data(
            **violation_out.model_dump(mode="json"),
            is_take=True,
            mo_start=current_time.isoformat(),
        )
    else:
        await state.update_data(
            **violation_out.model_dump(mode="json"),
            is_take=True,
        )

    text_mes = violation_out.violation_card()
    await state.update_data({
        f'vio_{violation_found_id}': violation_out.model_dump(mode='json')
    })
    await callback.message.answer(
        text=MoPerformerMessages.correct_mode(text_mes=text_mes),
        reply_markup=MoPerformerKeyboards().cancel_correct_mode(violation_found_id=violation_found_id)
    )
    await callback.answer()
    await state.set_state(MoPerformerStates.correct_violation)
    