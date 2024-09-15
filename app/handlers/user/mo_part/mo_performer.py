import asyncio
import datetime as dt

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, ReplyKeyboardRemove
from aiogram.utils.media_group import MediaGroupBuilder
from loguru import logger

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
from app.handlers.messages import DefaultMessages, MoPerformerMessages
from app.handlers.states import MoPerformerStates
from app.handlers.user.mo_part.performer_card_constructor import MoPerformerCard
from app.keyboards.mo_part import MoPerformerKeyboards

router = Router()
router.message.filter(MoPerformerFilter())


@router.message(Command('start'))
async def cmd_start(
    message: Message, state: FSMContext, user_obj: UserService = UserService()
):
    await state.clear()
    await user_obj.save_default_user_info(
        event=message,
        state=state
    )
    user = message.from_user
    logger.info(f'User {user.id} {user.username} passed authorization')
    await message.answer(
        text=await MoPerformerMessages.welcome_message(user_id=user.id),
        reply_markup=MoPerformerKeyboards().check_or_tasks(),
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text.lower() == 'активные проверки',
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_active_violations(
    message: Message, state: FSMContext,
    check_obj: CheckService = CheckService(),
    user_obj: UserService = UserService()
):
    await user_obj.save_default_user_info(
        event=message,
        state=state
    )
    data = await state.get_data()
    fil_ = data['fil_']
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    if not checks:
        await message.answer_sticker(
            sticker=MoPerformerMessages.find_sticker
        )
        await asyncio.sleep(1)
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
            reply_markup=message.reply_markup,
        )
    else:
        for check in checks:
            check_out = await check_obj.form_check_out(check=check)
            text_mes = check_out.form_card_check_out()
            keyboard = MoPerformerKeyboards().get_under_check(
                check_id=check.check_id
            ) if check_out.violations_count > 0 else MoPerformerKeyboards(
            ).get_under_check_zero_violations(
                check_id=check.check_id
            )
            await message.answer(text=text_mes, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith('violationszero_'),
    StateFilter(MoPerformerStates.mo_performer)
)
async def check_zero_violations(callback: CallbackQuery,
                                state: FSMContext,
                                check_obj: CheckService = CheckService()):
    check_id = str(callback.data.split('_')[1])
    data = await state.get_data()
    await callback.answer(
        text=MoPerformerMessages.finish_check_zero_violations,
        show_alert=True
    )
    current_time = dt.datetime.now(dt.timezone.utc)
    check_upd = CheckUpdate(
        mo_start=current_time if not data.get('mo_start') else dt.datetime.fromisoformat(data['mo_start']),
        mo_finish=current_time,
    )
    await check_obj.update_check(check_id=check_id, check_update=check_upd)
    await callback.message.delete()


@router.message(
    F.text.lower() == 'активные уведомления',
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_active_tasks(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    user_obj: UserService = UserService()
):
    await user_obj.save_default_user_info(
        event=message,
        state=state
    )

    data = await state.get_data()
    await state.update_data(
        mo_start=None
    )
    await violation_obj.update_data_violations_found_active(
        message=message,
        state=state,
        data=data,
    )
    data = await state.get_data()

    reply_obj = MoPerformerCard(data=data).all_violations_task_start(
    )
    if not reply_obj:
        await message.answer(
            text=MoPerformerMessages.form_no_tasks_answer(fil_=data['fil_']),
        )
    else:
        await message.answer_photo(
            **reply_obj.model_dump(mode='json')
        )


@router.message(
    F.text.lower() == 'перенесенные нарушения',
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_pending_violations_found(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    user_obj: UserService = UserService()
):
    await user_obj.save_default_user_info(
        event=message,
        state=state
    )
    data = await state.get_data()
    await violation_obj.update_data_violations_found_pending(
        message=message,
        state=state,
        data=data,
    )
    data = await state.get_data()
    reply_obj = MoPerformerCard(data=data).all_violations_pending_start()
    if not reply_obj:
        await message.answer(
            text=MoPerformerMessages.form_no_pending_violations_answer(fil_=data['fil_']),
        )
    else:
        await message.answer_photo(
            **reply_obj.model_dump(mode='json')
        )


@router.callback_query(
    F.data.startswith('take_') | F.data.startswith('correct_'),
    StateFilter(MoPerformerStates.correct_violation,
                MoPerformerStates.take_correct),
)
async def correct_first_violation(
    callback: CallbackQuery,
):
    await callback.answer(text=MoPerformerMessages.exit_first)


@router.callback_query(
    F.data.startswith('violations_'),
    StateFilter(MoPerformerStates.mo_performer)
)
async def get_check_violations(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    check_id = str(callback.data.split('_')[1])
    await state.update_data(
        check_id=check_id,
    )
    data = await state.get_data()
    await state.update_data(
        {
            k: None for k in data.keys() if k.startswith('vio_')
        }
    )
    data = await state.get_data()
    await violation_obj.update_data_violations_found_in_check(
        callback=callback,
        state=state,
        data=data
    )
    data_updated = await state.get_data()
    reply_obj = MoPerformerCard(data=data_updated).all_violations_check_start()
    if not reply_obj:
        await callback.message.answer(
            text=MoPerformerMessages.no_violations,
            reply_markup=MoPerformerKeyboards().check_finished()
        )
        await callback.answer()
        return

    await callback.message.answer_photo(
        **reply_obj.model_dump(mode='json')
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith('next_') | F.data.startswith('prev_'),
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_violations_next_prev(
    callback: CallbackQuery,
    state: FSMContext,
):
    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()

    violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])

    reply_obj = MoPerformerCard(data=data).get_next_prev_reply(
        violation_found_out=violation_found_obj
    )

    if not reply_obj:
        await callback.answer(text=MoPerformerMessages.no_violations_buttons)
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=reply_obj.photo,
                caption=reply_obj.caption),
            reply_markup=reply_obj.reply_markup
        )
        await callback.answer()


# @router.callback_query(
#     F.data.startswith('nphoto_') | F.data.startswith('pphoto_'),
#     StateFilter(MoPerformerStates.mo_performer),
# )
# async def get_photos_next_prev(
#     callback: CallbackQuery,
#     state: FSMContext,
# ):
#     violation_found_id = str(callback.data.split('_')[1])
#     data = await state.get_data()

#     violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
#     photo_ids = violation_found_obj.photo_id_mfc
#     if not photo_ids:
#         await callback.answer(text='Фото отсутствует')
#         return

#     current_photo_id = callback.message.photo[-1].file_id
#     logger.debug(f'Current_photo_id: {current_photo_id}')
#     try:
#         current_index = photo_ids.index(current_photo_id)
#     except ValueError:
#         logger.debug(f'VALUE_ERROR_ALL_IDS: {photo_ids}')
#         current_index = -1

#     if callback.data.startswith('nphoto_'):
#         next_index = (current_index + 1) % len(photo_ids)
#     else:
#         next_index = (current_index - 1) % len(photo_ids)

#     next_photo_id = photo_ids[next_index]
#     if (next_photo_id == current_photo_id) or (len(photo_ids) < 2):
#         await callback.answer(text='Больше фото для этого нарушения нет')
#     else:
#         try:
#             await callback.message.edit_media(
#                 media=InputMediaPhoto(
#                     media=next_photo_id,
#                     caption_entities=callback.message.caption_entities,
#                     caption=callback.message.caption,
#                     parse_mode=None
#                 ),
#                 reply_markup=callback.message.reply_markup
#             )
#         except TelegramBadRequest as e:
#             next_photo_id = photo_ids[current_index]
#             await callback.message.edit_media(
#                 media=InputMediaPhoto(
#                     media=next_photo_id,
#                     caption_entities=callback.message.caption_entities,
#                     caption=callback.message.caption,
#                     parse_mode=None
#                 ),
#                 reply_markup=callback.message.reply_markup
#             )
#         await callback.answer()


@router.callback_query(
    F.data.startswith('allphoto_'),
    ~StateFilter(MoPerformerStates.correct_violation)
    # StateFilter(MoPerformerStates.mo_performer)
)
async def get_all_photos(
    callback: CallbackQuery,
    state: FSMContext,
    vio_object: ViolationFoundService = ViolationFoundService()
):
    violation_found_id = str(callback.data.split('_')[1])
    mo_user_id = callback.message.from_user.id
    data = await state.get_data()
    vio_found_data_id = data.get(f'vio_{violation_found_id}')
    if not vio_found_data_id:
        violation_found_obj_in_db = await vio_object.get_violation_found_by_id(
            violation_found_id=violation_found_id
        )
        if not violation_found_obj_in_db:
            await callback.answer(text='Нарушение не найдено')
            return
        violation_found_obj = await vio_object.form_violation_out(
            violation=violation_found_obj_in_db,
            mo_user_id=mo_user_id
        )
    else:
        violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
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
        media=media_group.build()
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith('next_') | F.data.startswith('prev_'),
    ~StateFilter(MoPerformerStates.mo_performer),
)
async def wrong_state(callback: CallbackQuery):
    await callback.answer(text=DefaultMessages.not_good_time)


@router.callback_query(
    F.data.startswith('correct_'),
    StateFilter(MoPerformerStates.mo_performer)
)
async def process_correct_callback(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()
    is_fixed = await violation_obj.is_violation_already_fixed(
        violation_found_id=violation_found_id
    )
    if is_fixed:
        await callback.answer(text=MoPerformerMessages.violation_already_fixed)
        return

    violation_out = ViolationFoundOut(
        **data[f'vio_{violation_found_id}'],
    )
    await state.update_data(
        **violation_out.model_dump(mode='json')
    )
    data = await state.get_data()
    if data.get('is_task') or not data.get('mo_start'):
        current_time = dt.datetime.now(dt.timezone.utc)
        await state.update_data(
            mo_user_id=callback.from_user.id,
            mo_start=current_time.isoformat()
        )

    text_mes = violation_out.violation_card()

    await callback.message.answer(
        text=MoPerformerMessages.correct_mode(text_mes=text_mes),
        reply_markup=MoPerformerKeyboards().cancel_correct_mode(violation_found_id=violation_found_id),
    )
    await state.set_state(MoPerformerStates.correct_violation)
    await callback.answer()


@router.callback_query(
    F.data.startswith('cancel_'),
    StateFilter(MoPerformerStates.correct_violation)
)
async def process_cancel_correct(
    callback: CallbackQuery,
    state: FSMContext,
):
    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()

    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    await callback.message.delete()
    if violation_found_out.is_task:
        await state.update_data(
            {
                'mo_start': None
            }
        )

    await state.update_data(
        **ViolationFoundClearData().model_dump(mode='json')
    )

    await state.set_state(MoPerformerStates.mo_performer)


@router.message(F.photo,
                StateFilter(MoPerformerStates.correct_violation))
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
    await state.set_state(MoPerformerStates.save_vio_update)


@router.callback_query(
    F.data.startswith('cancelsave_'),
    StateFilter(MoPerformerStates.save_vio_update)
)
async def cancel_save_process(
    callback: CallbackQuery,
    state: FSMContext
):
    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()
    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])
    reply_obj = MoPerformerCard(data=data).cancel_process(
        violation_found_out=violation_found_out
    )

    if not reply_obj:
        await callback.answer(text=MoPerformerMessages.no_violations_buttons)
        return

    await callback.message.answer_photo(
        **reply_obj.model_dump(mode='json')
    )

    await callback.answer()
    if violation_found_out.is_task:
        await state.update_data(
            {
                'mo_start': None
            }
        )

    await state.update_data(
        **ViolationFoundClearData().model_dump(mode='json')
    )

    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text,
    StateFilter(MoPerformerStates.correct_violation,
                MoPerformerStates.take_correct)
)
async def add_text_wrong(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.exit_first
    )


@router.message(
    ~F.text & ~F.photo,
    StateFilter(MoPerformerStates.correct_violation,
                MoPerformerStates.take_correct)
)
async def wrong_add_content(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.only_photo_text
    )


@router.callback_query(
    F.data.startswith('save_'),
    StateFilter(MoPerformerStates.save_vio_update),
)
async def save_violation_found_process(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    is_pending = data.get('is_pending')
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

    if is_pending:
        await violation_obj.update_data_violations_found_pending(
            message=callback.message,
            state=state,
            data=data
        )
        data = await state.get_data()
        reply_obj = MoPerformerCard(data=data).all_violations_pending_start()
        await callback.answer()
        if not reply_obj:
            await callback.answer()
            await callback.message.answer(
                text=MoPerformerMessages.no_pending,
                reply_markup=MoPerformerKeyboards().back_to_menu(),
            )
        else:
            await callback.answer()
            await callback.message.answer_sticker(
                sticker=MoPerformerMessages.save_sticker,
            )
            await asyncio.sleep(1)
            await callback.message.answer(text=MoPerformerMessages.photo_comm_added)
            await callback.message.answer(
                text=MoPerformerMessages.can_continue_pending,
                reply_markup=MoPerformerKeyboards().back_to_menu(),
            )
            await asyncio.sleep(1)
            await callback.message.answer_photo(
                **reply_obj.model_dump(mode='json')
            )

    elif is_task:
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

        await violation_obj.update_data_violations_found_active(
            callback=callback,
            state=state,
            data=data
        )
        data = await state.get_data()
        reply_obj = MoPerformerCard(data=data).all_violations_task_start()
        if not reply_obj:
            await callback.answer()
            await callback.message.answer(
                text=MoPerformerMessages.tasks_work_finish,
            )
        else:
            await callback.answer()
            await callback.message.answer_sticker(
                sticker=MoPerformerMessages.save_sticker,
            )
            await asyncio.sleep(1)
            await callback.message.answer(text=MoPerformerMessages.photo_comm_added)
            await callback.message.answer_photo(
                **reply_obj.model_dump(mode='json')
            )

    else:
        await callback.answer()
        await callback.message.answer_sticker(
            sticker=MoPerformerMessages.save_sticker,
        )
        await asyncio.sleep(1)
        await callback.message.answer(text=MoPerformerMessages.photo_comm_added)
        await asyncio.sleep(1)
        await callback.message.answer(
            text=MoPerformerMessages.can_continue_check,
            reply_markup=MoPerformerKeyboards().back_to_violations(),
        )

    await state.set_state(MoPerformerStates.mo_performer)


@router.message(
    F.text.lower() == 'вернуться в меню', StateFilter(MoPerformerStates.mo_performer)
)
async def back_to_menu(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.choose_check_task,
        reply_markup=MoPerformerKeyboards().check_or_tasks(),
    )


@router.message(
    F.text.lower() == 'вернуться в меню', StateFilter(MoPerformerStates.correct_violation)
)
async def back_to_menu_from_correct(
    message: Message,
):
    await message.answer(
        text=MoPerformerMessages.exit_first,
    )


@router.message(
    F.text.lower() == 'продолжить проверку',
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_continue(
    message: Message,
    state: FSMContext,
):
    await message.answer(
        text=MoPerformerMessages.continue_check, reply_markup=ReplyKeyboardRemove()
    )
    await asyncio.sleep(1)
    data = await state.get_data()
    reply_obj = MoPerformerCard(data=data).all_violations_check_start()
    if not reply_obj:
        await message.answer(
            text=MoPerformerMessages.no_violations,
            reply_markup=MoPerformerKeyboards().check_finished(),
        )
    else:
        await message.answer_photo(
            **reply_obj.model_dump(mode='json')
        )


@router.message(
    F.text.lower() == 'закончить проверку',
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_finish(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    check_id = data['check_id']
    logger.debug(f'check_id_is: {check_id}')
    violation_out_objects = MoPerformerCard(data=data).get_current_check_violations(check_id=check_id)
    logger.debug(f'check_id_is: {check_id}')
    logger.debug(f'VIO_OUT: {violation_out_objects}')
    if violation_out_objects:
        await message.answer(
            text=MoPerformerMessages.cant_finish, reply_markup=message.reply_markup
        )
        return
    current_time = dt.datetime.now(dt.timezone.utc)
    check_upd = CheckUpdate(
        mo_start=current_time if not data.get('mo_start') else dt.datetime.fromisoformat(data['mo_start']),
        mo_finish=current_time,
    )
    await check_obj.update_check(check_id=check_id, check_update=check_upd)
    await state.update_data(mo_start=None)
    fil_ = data['fil_']
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    await message.answer(
        text=MoPerformerMessages.finish_check_zero_violations,
    )
    await message.answer(
        text=MoPerformerMessages.back_to_checks,
        reply_markup=MoPerformerKeyboards().check_or_tasks(),
    )
    await asyncio.sleep(1)

    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
    else:
        for check in checks:
            check_out = await check_obj.form_check_out(check=check)
            text_mes = check_out.form_card_check_out()
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.check_id)
            await message.answer(text=text_mes, reply_markup=keyboard)


@router.message()
async def something_wrong(message: Message):
    await message.answer(text=DefaultMessages.something_wrong)


@router.callback_query()
async def something_wrong_callback(callback: CallbackQuery):
    await callback.answer(text=DefaultMessages.not_good_time)
