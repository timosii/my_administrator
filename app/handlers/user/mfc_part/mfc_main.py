import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message, ReplyKeyboardRemove
from aiogram_media_group import media_group_handler
from loguru import logger

from app.database.schemas.violation_found_schema import (
    ViolationFoundClearInfo,
    ViolationFoundCreate,
    ViolationFoundDeleteMfc,
    ViolationFoundOut,
)
from app.database.services.check import CheckService
from app.database.services.helpers import HelpService
from app.database.services.violations_found import ViolationFoundService
from app.filters.default import not_constants
from app.filters.form_menu import (
    IsInFilials,
    IsInMos,
    IsInProblems,
    IsInViolations,
    IsInZones,
)
from app.filters.mfc_filters import MfcFilter
from app.handlers.messages import DefaultMessages, MfcMessages
from app.handlers.states import MfcStates
from app.handlers.user.mfc_part.mfc_pending_logic import MfcPendingCard
from app.keyboards.default import DefaultKeyboards
from app.keyboards.mfc_part import MfcKeyboards

router = Router()
router.message.filter(MfcFilter())


@router.message(Command('start'))
async def cmd_start(
    message: Message,
    state: FSMContext,
    violation_found_obj: ViolationFoundService = ViolationFoundService()
):
    user = message.from_user
    logger.info(f'User {user.id} {user.username} passed authorization')
    await state.clear()
    await state.update_data(mfc_user_id=user.id)
    await violation_found_obj.user_empty_violations_found_process(user_id=user.id)
    await message.answer(
        text=await MfcMessages.welcome_message(user_id=user.id),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(MfcStates.choose_mo)


@router.message(Command('menu'))
async def cmd_menu(
    message: Message,
    state: FSMContext,
    violation_found_obj: ViolationFoundService = ViolationFoundService()
):
    user = message.from_user
    logger.info(f'User {user.id} {user.username} passed authorization')
    await state.update_data(
        mfc_user_id=user.id,
        violations_completed={})
    data = await state.get_data()
    mo = data.get('mo')
    fil = data.get('fil_')
    if not (mo and fil):
        await message.answer(
            text=MfcMessages.please_start,
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await violation_found_obj.user_empty_violations_found_process(user_id=user.id)
    await message.answer(
        text=MfcMessages.main_menu,
        reply_markup=await MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.message(
    F.text,
    not_constants,
    StateFilter(MfcStates.choose_mo)
)
async def choose_mo(message: Message,
                    state: FSMContext,
                    helper: HelpService = HelpService()
                    ):
    num = message.text.capitalize()
    mos = await helper.mo_define_by_num(num=num)
    if not mos:
        await message.answer(
            text=DefaultMessages.does_not_find
        )
        return
    elif len(mos) > 1:
        await message.answer(
            text=DefaultMessages.choose_mo_additional,
            reply_markup=DefaultKeyboards().choose_mo(mos=mos),
        )
        await state.set_state(MfcStates.choose_mo_additional)

    else:
        mo = mos[0]
        await message.answer(
            text=DefaultMessages.choose_fil(mo=mo),
            reply_markup=await DefaultKeyboards().choose_fil(mo=mo),
        )
        await state.update_data(mo=mo)
        await state.set_state(MfcStates.choose_fil)


@router.message(
    IsInMos(),
    StateFilter(MfcStates.choose_mo_additional)
)
async def choose_mo_additional(message: Message, state: FSMContext):
    mo = message.text
    await message.answer(
        text=DefaultMessages.choose_fil(mo=mo),
        reply_markup=await DefaultKeyboards().choose_fil(mo=mo),
    )
    await state.update_data(mo=mo)
    await state.set_state(MfcStates.choose_fil)


@router.message(
    ~IsInMos(),
    F.text,
    not_constants,
    StateFilter(MfcStates.choose_mo_additional)
)
async def wrong_choose_mos_additional(message: Message):
    await message.answer(
        text=DefaultMessages.choose_mo_additional,
        reply_markup=message.reply_markup
    )


@router.message(
    F.text.lower() == 'назад',
    StateFilter(MfcStates.choose_mo_additional)
)
async def back_choose_mos_additional(
    message: Message,
    state: FSMContext
):
    user = message.from_user
    await message.answer(
        text=await MfcMessages.welcome_message(user_id=user.id),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(MfcStates.choose_mo)


@router.message(
    ~F.text,
    StateFilter(MfcStates.choose_mo_additional),
    StateFilter(MfcStates.choose_mo),
    StateFilter(MfcStates.choose_fil)
)
async def wrong_type(message: Message):
    await message.answer(
        text=MfcMessages.wrong_type
    )


@router.message(
    IsInFilials(),
    StateFilter(MfcStates.choose_fil)
)
async def choose_fil_handler(
    message: Message,
    state: FSMContext,
):
    await state.update_data(fil_=message.text)
    await message.answer(
        text=MfcMessages.main_menu,
        reply_markup=await MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.message(
    F.text.lower() == 'начать проверку', StateFilter(MfcStates.choose_type_checking)
)
async def start_checking_process(
    message: Message,
    state: FSMContext,
    check: CheckService = CheckService(),
):
    await check.start_checking_process(
        message=message,
        state=state,
        is_task=False
    )


@router.message(
    F.text.lower() == 'проверить незавершенные проверки',
    StateFilter(MfcStates.choose_type_checking),
)
async def get_unfinished_checks(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    checks = await check_obj.get_mfc_fil_active_checks(fil_=data['fil_'])
    await check_obj.unfinished_checks_process(
        message=message, state=state, checks=checks
    )


@router.callback_query(
    F.data.startswith('delete_unfinished_check_'), MfcStates.choose_type_checking
)
async def delete_unfinished(
    callback: CallbackQuery, state: FSMContext, check_obj: CheckService = CheckService()
):
    check_id = str(callback.data.split('_')[-1])
    violation_count = await check_obj.get_violations_found_count_by_check(check_id=check_id)
    if violation_count == 0:
        await check_obj.delete_check(check_id=check_id)
        await callback.answer(
            text=MfcMessages.check_deleted,
        )
        await state.update_data({
            f'check_unfinished_{check_id}': None
        })
        await callback.message.delete()
    else:
        await callback.answer(
            text=MfcMessages.cant_delete,
            show_alert=True
        )


@router.callback_query(
    F.data.startswith('finish_unfinished_check_'), MfcStates.choose_type_checking
)
async def finish_unfinished(
    callback: CallbackQuery, state: FSMContext, check_obj: CheckService = CheckService()
):
    check_id = str(callback.data.split('_')[-1])
    await check_obj.finish_unfinished_process(
        state=state, callback=callback, check_id=check_id
    )
    await callback.message.answer(
        text=MfcMessages.choose_zone,
        reply_markup=await MfcKeyboards().choose_zone()
    )
    await state.set_state(MfcStates.choose_zone)


@router.message(
    F.text.lower() == 'добавить уведомление о нарушении',
    StateFilter(MfcStates.choose_type_checking),
)
async def notification_handler(
    message: Message,
    state: FSMContext,
    check: CheckService = CheckService(),
):
    await check.start_checking_process(
        message=message,
        state=state,
        is_task=True
    )


@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    user = message.from_user
    if current_state == MfcStates.choose_fil:
        await state.set_state(MfcStates.choose_mo)
        await state.update_data(
            mo=None,
            mfc_user_id=message.from_user.id
        )
        await message.answer(
            text=await MfcMessages.welcome_message(user_id=user.id), reply_markup=ReplyKeyboardRemove()
        )
    elif current_state == MfcStates.choose_type_checking:
        await state.set_state(MfcStates.choose_fil)
        data = await state.get_data()
        mo = data['mo']
        await message.answer(
            text=DefaultMessages.choose_fil(mo=mo),
            reply_markup=await DefaultKeyboards().choose_fil(mo=mo),
        )
        await state.update_data(
            fil_=None,
        )
    else:
        await message.answer(
            text=DefaultMessages.something_wrong,
            reply_markup=message.reply_markup,
        )


@router.message(
    IsInZones(),
    StateFilter(MfcStates.choose_zone)
)
async def choose_zone_handler(message: Message, state: FSMContext):
    zone = ' '.join(message.text.split()[1:])
    data = await state.get_data()
    fil: str = data['fil_']
    zones_completed: dict = data.get('violations_completed', {})
    violations_completed: list = zones_completed.get(zone, {}).keys()
    await message.answer(
        text=await MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(
            zone=zone,
            fil=fil,
            completed_violations=violations_completed),
    )
    await state.update_data(
        zone=zone
    )
    await state.set_state(MfcStates.choose_violation)


@router.message(
    IsInViolations(),
    StateFilter(MfcStates.choose_violation),
)
async def choose_violation_handler(
    message: Message,
    state: FSMContext,
):
    violation_name = message.text
    if '✅' in violation_name:
        violation_name = message.text.split('✅')[-1].strip()

    data = await state.get_data()
    zone = data['zone']
    zones_completed: dict = data.get('violations_completed', {})
    violations_completed: dict = zones_completed.get(zone, {})
    completed_problems: list = violations_completed.get(violation_name, [])

    await message.answer(
        text=await MfcMessages.choose_problem(violation_name=violation_name, zone=zone),
        reply_markup=await MfcKeyboards().choose_problem(
            violation_name=violation_name,
            zone=zone,
            completed_problems=completed_problems
        ),
    )
    await state.update_data(
        violation_name=violation_name,
        zone=zone
    )
    await state.set_state(MfcStates.choose_problem)


@router.message(
    IsInProblems(),
    StateFilter(MfcStates.choose_problem),
)
async def choose_problem_handler(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    problem_name = message.text
    if '✅' in problem_name:
        problem_name = message.text.split('✅')[-1].strip()

    data = await state.get_data()
    violation_name = data['violation_name']
    zone = data['zone']
    violation_dict_id = await violation_obj.get_dict_id_by_name(
        violation_name=violation_name,
        zone=zone,
        problem=problem_name,
    )
    await state.update_data(
        problem=problem_name,
        violation_dict_id=violation_dict_id,
    )
    violation_create_obj = ViolationFoundCreate(
        **(await state.get_data()),
    )

    is_violation_already_in_check = (
        await violation_obj.is_violation_already_in_check(
            violation_dict_id=violation_dict_id,
            check_id=violation_create_obj.check_id,
        )
    )
    if is_violation_already_in_check:
        await message.answer(
            text=MfcMessages.violation_already_in_check,
            reply_markup=message.reply_markup,
        )
        return

    violations_pending_by_dict_id = await violation_obj.get_pending_violations_by_fil_n_dict_id(
        fil_=data['fil_'],
        violation_dict_id=violation_dict_id
    )
    if violations_pending_by_dict_id:
        await MfcPendingCard().save_to_data_process(
            state=state,
            pending_violations_in=violations_pending_by_dict_id
        )
        violations_out = await MfcPendingCard().get_violations_out_from_data(state=state)
        reply_obj = await MfcPendingCard().form_reply(violations_out=violations_out)
        await message.answer(
            text=MfcMessages.add_violation_whatever,
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer_sticker(
            sticker=MfcMessages.watch_sticker
        )
        await asyncio.sleep(7)
        await message.answer_photo(
            **reply_obj.model_dump(mode='json')
        )
        await state.set_state(MfcStates.get_pending)
        return

    violation_in_db = await violation_obj.add_violation(violation_create=violation_create_obj)
    violation_out = await violation_obj.form_violation_out(violation=violation_in_db)
    await state.update_data(
        violation_out.model_dump(mode='json')
    )

    await message.answer(
        text=MfcMessages.problem_detection,
        reply_markup=await MfcKeyboards().just_cancel()
    )
    await message.answer(
        text=await MfcMessages.add_photo_comm(
            zone=zone,
            violation_name=violation_name,
            problem=problem_name),
        # reply_markup=await MfcKeyboards().get_description(violation_id=violation_out.violation_dict_id),
    )
    await state.set_state(MfcStates.add_content)


@router.callback_query(
    F.data.startswith('next_') | F.data.startswith('prev_'),
    StateFilter(MfcStates.get_pending),
)
async def get_violations_next_prev(
    callback: CallbackQuery,
    state: FSMContext,
):
    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()

    violation_found_out = ViolationFoundOut(**data[f'vio_{violation_found_id}'])

    reply_obj = await MfcPendingCard().get_next_prev_reply(
        state=state,
        violation_found_out=violation_found_out
    )

    if not reply_obj:
        await callback.answer(text=MfcMessages.no_violations)
    else:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=reply_obj.photo,
                caption=reply_obj.caption),
            reply_markup=reply_obj.reply_markup
        )
        await callback.answer()


@router.callback_query(
    F.data.startswith('allphoto_'),
    StateFilter(MfcStates.get_pending)
)
async def get_all_photos(
    callback: CallbackQuery,
    state: FSMContext,
):

    violation_found_id = str(callback.data.split('_')[1])
    data = await state.get_data()
    violation_found_obj = ViolationFoundOut(**data[f'vio_{violation_found_id}'])

    await ViolationFoundService.get_all_photos(
        callback=callback,
        violation_found_obj=violation_found_obj
    )


@router.callback_query(
    F.data.startswith('back_'),
    StateFilter(MfcStates.get_pending),
)
async def get_back(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    zones_completed: dict = data.get('violations_completed', {})
    violations_completed: dict = zones_completed.get(zone, {})
    completed_problems: list = violations_completed.get(violation_name, [])
    await state.update_data(
        {
            k: None for k, _ in data.items() if k.startswith('vio_')
        }
    )
    await callback.message.answer(
        text=await MfcMessages.choose_problem(violation_name=violation_name, zone=zone),
        reply_markup=await MfcKeyboards().choose_problem(
            violation_name=violation_name,
            zone=zone,
            completed_problems=completed_problems),
    )
    await callback.answer()
    await state.set_state(MfcStates.choose_problem)


@router.callback_query(
    F.data.startswith('new_'),
    StateFilter(MfcStates.get_pending),
)
async def add_new_violation(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService()
):
    violation_create_obj = ViolationFoundCreate(
        **(await state.get_data()),
    )

    violation_in_db = await violation_obj.add_violation(violation_create=violation_create_obj)
    violation_out = await violation_obj.form_violation_out(violation=violation_in_db)
    await state.update_data(
        violation_out.model_dump(mode='json')
    )
    data = await state.get_data()
    await state.update_data(
        {
            k: None for k, _ in data.items() if k.startswith('vio_')
        }
    )

    await callback.message.answer(
        text=MfcMessages.problem_detection,
        reply_markup=await MfcKeyboards().just_cancel()
    )
    await callback.message.answer(
        text=await MfcMessages.add_photo_comm(
            zone=violation_out.zone,
            violation_name=violation_out.violation_name,
            problem=violation_out.problem,
        ),
        # reply_markup=await MfcKeyboards().get_description(violation_id=violation_out.violation_dict_id),
    )
    await callback.answer()
    await state.set_state(MfcStates.add_content)


@router.message(
    F.photo,
    StateFilter(MfcStates.add_content)
)
async def add_photo_comm_directly(
    message: Message,
    state: FSMContext
):
    photo_id_mfc = message.photo[-1].file_id
    comm_mfc = message.caption
    if not comm_mfc:
        await message.answer(
            text=MfcMessages.not_comm_to_photo
        )
        return
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    problem = data['problem']
    await state.update_data(
        photo_id_mfc=[photo_id_mfc],
        comm_mfc=comm_mfc
    )
    await message.answer(
        text=await MfcMessages.photo_comm_added(
            zone=zone,
            violation_name=violation_name,
            problem=problem
        ),
        reply_markup=await MfcKeyboards().save_or_cancel(),
    )
    await state.set_state(MfcStates.continue_state)


@router.callback_query(
    F.data == 'additional_photo',
    StateFilter(MfcStates.continue_state)
)
async def add_photo_additional(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    problem = data['problem']
    await callback.message.answer(
        text=await MfcMessages.photo_additional(
            zone=zone,
            violation_name=violation_name,
            problem=problem
        ),
        reply_markup=await MfcKeyboards().finish_photo_addition(),
    )
    await callback.answer()
    await state.set_state(MfcStates.additional_photo)


@router.message(
    F.media_group_id,
    F.content_type.in_({'photo'}),
    StateFilter(MfcStates.additional_photo))
@media_group_handler
async def add_photo_media_group(
    messages: list[Message],
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()
    photos_ids = data.get('photo_id_mfc', [])
    can_add = 10 - len(photos_ids)
    if can_add == 0:
        await bot.send_message(
            chat_id=messages[0].chat.id,
            text=MfcMessages.cant_add_photo,
            reply_markup=await MfcKeyboards().finish_photo_addition(),
        )
        return

    photos_ids_add = [m.photo[-1].file_id for m in messages]
    if len(photos_ids_add) > can_add:
        photos_ids_add = photos_ids_add[:can_add]

    photos_ids.extend(photos_ids_add)

    await state.update_data(
        photo_id_mfc=photos_ids,
    )
    await bot.send_message(
        chat_id=messages[0].chat.id,
        text='Фотографии добавлены!',
        reply_markup=await MfcKeyboards().finish_photo_addition(),
    )


@router.message(
    F.photo,
    StateFilter(MfcStates.additional_photo)
)
async def add_photo_add(
    message: Message,
    state: FSMContext
):
    photo_id_mfc = message.photo[-1].file_id
    data = await state.get_data()
    photos_ids = data.get('photo_id_mfc', [])
    can_add = 10 - len(photos_ids)
    if can_add == 0:
        await message.answer(
            text=MfcMessages.cant_add_photo,
            reply_markup=await MfcKeyboards().finish_photo_addition(),
        )
        return

    photos_ids = data.get('photo_id_mfc', [])
    photos_ids.append(photo_id_mfc)
    await state.update_data(
        photo_id_mfc=photos_ids,
    )
    await message.answer(
        text=MfcMessages.photo_added,
        reply_markup=await MfcKeyboards().finish_photo_addition(),
    )


@router.message(
    F.text.lower() == 'закончить добавление фото',
    StateFilter(MfcStates.additional_photo)
)
async def finish_additional_photo(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    problem = data['problem']
    await message.answer(
        text=MfcMessages.violation_saved,
        reply_markup=await MfcKeyboards().just_cancel()
    )
    await message.answer(
        text=await MfcMessages.photo_additional_added(
            zone=zone,
            violation_name=violation_name,
            problem=problem,
        ),
        reply_markup=await MfcKeyboards().save_or_cancel(),
    )
    await state.set_state(MfcStates.continue_state)


@router.message(
    F.text,
    not_constants,
    StateFilter(MfcStates.add_content)
)
async def add_text_only_directly(
    message: Message,
):
    await message.answer(
        text=MfcMessages.need_comm_and_photo
    )


@router.message(
    ~F.text & ~F.photo,
    StateFilter(MfcStates.add_content)
)
async def wrong_add_content(
    message: Message,
):
    await message.answer(
        text=MfcMessages.work_only_with_photo_and_text
    )


@router.message(
    F.text.lower() == '⬅️ к выбору зоны',
    StateFilter(MfcStates.choose_violation),
)
async def to_zone_choose(
    message: Message,
    state: FSMContext,
):
    await state.set_state(MfcStates.choose_zone)
    await message.answer(
        text=MfcMessages.choose_zone,
        reply_markup=await MfcKeyboards().choose_zone()
    )
    await state.update_data(zone=None)


@router.message(
    F.text.lower() == '⬅️ к выбору нарушения',
    StateFilter(MfcStates.choose_problem),
)
async def to_violation_choose(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    zone: str = data['zone']
    fil: str = data['fil_']
    zones_completed: dict = data.get('violations_completed', {})
    violations_completed: list = zones_completed.get(zone, {}).keys()
    await state.set_state(MfcStates.choose_violation)
    await message.answer(
        text=await MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(
            zone=zone,
            fil=fil,
            completed_violations=violations_completed,
        ),
    )
    await state.update_data(violation_name=None)
    await state.set_state(MfcStates.choose_violation)


# @router.callback_query(
#     F.data.startswith('description_'),
#     ~StateFilter(default_state))
# async def get_description(
#     callback: CallbackQuery,
#     violation_dict_obj: ViolationFoundService = ViolationFoundService(),
# ):
#     violation_id = int(callback.data.split('_')[-1])
#     result = await violation_dict_obj.get_description(violation_dict_id=violation_id)
#     if result:
#         try:
#             await callback.answer(text=result, show_alert=True)
#         except TelegramBadRequest:
#             await callback.message.answer(text=result)
#             await callback.answer()
#     else:
#         await callback.answer(text=MfcMessages.no_description, show_alert=True)


@router.message(
    F.text.lower() == 'отменить',
    StateFilter(MfcStates.continue_state),
)
async def cancel_adding(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    problem = data['problem']
    # violation_dict_id = data['violation_dict_id']
    await message.answer(
        text=await MfcMessages.add_photo_comm(
            zone=zone,
            violation_name=violation_name,
            problem=problem
        ),
        # reply_markup=await MfcKeyboards().get_description(violation_id=violation_dict_id),
    )

    await state.update_data(comm_mfc=None, photo_id_mfc=None)
    await state.set_state(MfcStates.add_content)


@router.message(F.text.lower() == 'отменить',
                StateFilter(MfcStates.add_content))
async def cancel_adding_vio(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService()
):
    await state.set_state(MfcStates.choose_problem)
    data = await state.get_data()
    zone = data['zone']
    violation_name = data['violation_name']
    violation_found_id = data['violation_found_id']
    zones_completed: dict = data.get('violations_completed', {})
    violations_completed: dict = zones_completed.get(zone, {})
    completed_problems: list = violations_completed.get(violation_name, [])

    await violation_obj.delete_violation(
        violation_id=violation_found_id
    )
    await state.update_data(
        time_to_correct=None,
        violation_detected=None,
        violation_found_id=None,
        problem=None,
        # violation_name=None,
        violation_dict_id=None
    )
    await message.answer(
        text=await MfcMessages.choose_problem(
            violation_name=violation_name,
            zone=zone,
        ),
        reply_markup=await MfcKeyboards().choose_problem(
            violation_name=violation_name,
            zone=zone,
            completed_problems=completed_problems,
        )
    )


@router.callback_query(F.data == 'save_and_go',
                       StateFilter(MfcStates.continue_state))
async def save_violation(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    violation_found_out = ViolationFoundOut(
        **data
    )
    zone = violation_found_out.zone
    violation_name = violation_found_out.violation_name
    problem = violation_found_out.problem

    await violation_obj.save_violation_process(
        callback=callback,
        violation_found_out=violation_found_out,
    )

    await violation_obj.send_vio_notification_to_fil_performers(
        callback=callback,
        violation=violation_found_out
    )

    await callback.answer(text=MfcMessages.violation_saved, show_alert=True)
    violations_completed: dict = data.get('violations_completed', {})
    zone_violations: dict = violations_completed.setdefault(zone, {})
    zone_violations.setdefault(violation_name, [])
    violations_completed[zone][violation_name].append(problem)
    await state.update_data(violations_completed=violations_completed)

    if data.get('is_task'):
        check_id = data['check_id']
        await check_obj.finish_check_process(
            state=state,
            check_id=check_id
        )
        await state.update_data(
            **ViolationFoundClearInfo().model_dump()
        )
        await callback.message.answer(
            text=MfcMessages.cancel_check,
            reply_markup=await MfcKeyboards().main_menu()
        )
        await state.set_state(MfcStates.choose_type_checking)
        return

    await callback.message.answer(
        text=MfcMessages.continue_check,
    )

    await asyncio.sleep(1)

    data = await state.get_data()

    zones_completed: dict = data.get('violations_completed', {})
    violations_completed_: dict = zones_completed.get(zone, {})
    completed_problems: list = violations_completed_.get(violation_name, [])

    await callback.message.answer(
        text=await MfcMessages.choose_problem(zone=zone, violation_name=violation_name),
        reply_markup=await MfcKeyboards().choose_problem(
            zone=zone,
            violation_name=violation_name,
            completed_problems=completed_problems,
        )
    )
    await state.update_data(
        **ViolationFoundDeleteMfc().model_dump()
    )
    await state.set_state(MfcStates.choose_problem)


@router.message(
    F.text.lower() == '⛔️ закончить проверку', StateFilter(MfcStates.choose_zone)
)
async def finish_check(
    message: Message, state: FSMContext,
    check_obj: CheckService = CheckService()
):
    data = await state.get_data()
    check_id = data.get('check_id')
    violation_count = await check_obj.get_violations_found_count_by_check(check_id=check_id)
    if data['is_task']:
        if violation_count == 0:
            await check_obj.delete_check(check_id=check_id)
            await message.answer(
                text=MfcMessages.finish_task_zero_violations,
                reply_markup=await MfcKeyboards().main_menu()
            )
        else:
            await message.answer_sticker(
                sticker=MfcMessages.save_sticker
            )
            await asyncio.sleep(1)
            await message.answer(
                text=MfcMessages.notification_saved,
                reply_markup=await MfcKeyboards().main_menu()
            )
        await state.update_data(
            **ViolationFoundClearInfo().model_dump()
        )
        await state.set_state(MfcStates.choose_type_checking)
        return

    await check_obj.finish_check_process(
        state=state,
        check_id=check_id
    )
    await message.answer_sticker(
        sticker=MfcMessages.save_sticker
    )
    await asyncio.sleep(1)
    await message.answer(
        text=MfcMessages.finish_check,
        reply_markup=await MfcKeyboards().main_menu()
    )
    await state.update_data(
        **ViolationFoundClearInfo().model_dump()
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.callback_query(StateFilter(MfcStates))
async def something_wrong_callback(callback: CallbackQuery):
    await callback.answer(text=DefaultMessages.not_good_time)
