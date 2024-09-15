import asyncio
import datetime as dt

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.database.schemas.check_schema import CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundClearData,
    ViolationFoundOut,
    ViolationFoundUpdate,
)
from app.database.services.check import CheckService
from app.database.services.users import UserService
from app.database.services.violations_found import ViolationFoundService
from app.filters.mo_filters import MoPerformerFilter
from app.handlers.messages import MoPerformerMessages
from app.handlers.states import MoPerformerStates
from app.keyboards.mo_part import MoPerformerKeyboards

router = Router()
router.message.filter(MoPerformerFilter())


@router.callback_query(
    F.data.startswith('take_'),
    ~StateFilter(MoPerformerStates.correct_violation)
)
async def take_to_work(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    user_obj: UserService = UserService()
):
    await state.clear()
    await user_obj.save_default_user_info(
        event=callback,
        state=state,
    )
    violation_found_id = str(callback.data.split('_')[1])
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
    if not violation_in_db:
        return
    data = await state.get_data()
    mo_user_id = data['mo_user_id']
    violation_out = await violation_obj.form_violation_out(
        mo_user_id=mo_user_id,
        violation=violation_in_db)
    current_time = dt.datetime.now(dt.timezone.utc)
    if violation_out.is_task:
        await state.update_data(
            **violation_out.model_dump(mode='json'),
            is_take=True,
            mo_start=current_time.isoformat(),
        )
    else:
        await state.update_data(
            **violation_out.model_dump(mode='json'),
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
    await state.set_state(MoPerformerStates.take_correct)


# @router.callback_query(
#     F.data.startswith('allphoto_'),
#     StateFilter(MoPerformerStates.mo_performer)
# )
# async def get_all_photos(
#     callback: CallbackQuery,
#     state: FSMContext,
# ):
#     violation_found_id = str(callback.data.split('_')[1])
#     data = await state.get_data()
#     violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
#     photo_ids = violation_found_obj.photo_id_mfc
#     if not photo_ids:
#         await callback.answer(text='Фотографий нет')
#         return

#     if len(photo_ids) < 2:
#         await callback.answer(text='Больше фотографий нет')
#         return

#     if len(photo_ids) > 10:
#         photo_ids = photo_ids[:10]

#     violation_name = violation_found_obj.violation_name
#     media_group = MediaGroupBuilder(caption=violation_name)
#     for photo_id in photo_ids:
#         media_group.add_photo(media=photo_id)
#     await callback.message.answer_media_group(
#         media=media_group.build()
#     )
#     await callback.answer()

@router.message(F.photo,
                StateFilter(MoPerformerStates.take_correct))
async def add_photo_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    violation_found_id = data['violation_found_id']
    photo_id_mo = message.photo[-1].file_id
    comm_mo = message.caption
    if not comm_mo:
        await message.answer(
            text=MoPerformerMessages.no_photo_added
        )
        return
    comm_mo_presence = data.get('comm_mo')
    await state.update_data({
        'photo_id_mo': photo_id_mo,
        'comm_mo': comm_mo if not comm_mo_presence else (comm_mo_presence + '\n\nПри исправлении:\n' + comm_mo)
    })
    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    await message.answer(
        text=MoPerformerMessages.finish_mes(violation_found_out.violation_name),
        reply_markup=MoPerformerKeyboards().save_violation_found(
            violation_found_id=violation_found_id
        ),
    )
    await state.set_state(MoPerformerStates.take_save)


@router.callback_query(
    F.data.startswith('cancel_'),
    StateFilter(MoPerformerStates.take_correct)
)
async def process_cancel_take_correct(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer(text=MoPerformerMessages.exit_take)
    await callback.message.delete()
    await state.clear()
    await state.set_state(MoPerformerStates.mo_performer)


@router.callback_query(
    F.data.startswith('save_'),
    StateFilter(MoPerformerStates.take_save),
)
async def save_violation_found_process(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    is_task = data.get('is_task')
    violation_found_id = str(callback.data.split('_')[1])
    current_time = dt.datetime.now(dt.timezone.utc)
    vio_upd = ViolationFoundUpdate(
        mo_user_id=data['mo_user_id'],
        photo_id_mo=data['photo_id_mo'],
        comm_mo=data['comm_mo'],
        violation_fixed=current_time,
    )
    await violation_obj.update_violation(
        violation_found_id=violation_found_id,
        violation_update=vio_upd
    )
    await state.update_data({
        f'vio_{violation_found_id}': None,
    })
    await state.update_data(
        **ViolationFoundClearData().model_dump(mode='json')
    )
    data = await state.get_data()

    if is_task:
        check_id = data['check_id']
        current_time = dt.datetime.now(dt.timezone.utc)
        check_upd = CheckUpdate(
            mo_start=dt.datetime.fromisoformat(data['mo_start']),
            mo_finish=current_time,
        )
        await check_obj.update_check(check_id=check_id, check_update=check_upd)
        await state.update_data(
            mo_start=None,
            check_id=None
        )

    await callback.answer()
    await callback.message.answer_sticker(
        sticker=MoPerformerMessages.save_sticker,
    )
    await asyncio.sleep(1)
    await callback.message.answer(text=MoPerformerMessages.photo_comm_added)
    await state.set_state(MoPerformerStates.mo_performer)


@router.callback_query(
    F.data.startswith('cancelsave_'),
    StateFilter(MoPerformerStates.take_save)
)
async def cancel_save_process(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer(text=MoPerformerMessages.exit_take)
    await callback.message.edit_text(text=MoPerformerMessages.exit_take_save)
    await state.clear()
    await state.set_state(MoPerformerStates.mo_performer)
