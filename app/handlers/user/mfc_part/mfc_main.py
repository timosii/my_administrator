import json
import datetime as dt
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MfcMessages, DefaultMessages
from app.handlers.states import MfcStates
from app.filters.mfc_filters import MfcFilter
from app.filters.default import not_back_filter, not_cancel_filter, not_buttons_filter
from app.filters.form_menu import is_in_filials, is_in_violations, is_in_zones
# from app.database.db_helpers.form_menu import get_zones, get_violations, get_filials
# from app.database.db_helpers.form_menu import ZONES, VIOLATIONS, FILIALS
from app.database.services.users import UserService
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.schemas.check_schema import CheckCreate, CheckInDB, CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundOut,
)
from loguru import logger
from aiogram.exceptions import TelegramBadRequest
import pytz
from app.utils.utils import to_moscow_time



router = Router()
router.message.filter(MfcFilter())
# moscow_tz = pytz.timezone('Europe/Moscow')

# @router.message(F.text.lower() == "пройти авторизацию", StateFilter(default_state))
# async def cmd_start(
#     message: Message, state: FSMContext, user_obj: UserService = UserService()
# ):
#     user = message.from_user
#     mo = await user_obj.get_user_mo(user_id=user.id)
#     await state.update_data(mfc_user_id=user.id, mo=mo)
#     logger.info("User {0} {1} passed authorization".format(user.id, user.username))
#     await message.answer(
#         text=MfcMessages.welcome_message,
#         reply_markup=await MfcKeyboards().choose_fil(mo=mo),
#     )
#     await state.set_state(MfcStates.choose_fil)

@router.message(Command('start'))
async def cmd_start(
    message: Message, state: FSMContext, user_obj: UserService = UserService()
):
    user = message.from_user
    mo = await user_obj.get_user_mo(user_id=user.id)
    await state.update_data(mfc_user_id=user.id, mo=mo)
    logger.info("User {0} {1} passed authorization".format(user.id, user.username))
    await message.answer(
        text=MfcMessages.welcome_message,
        reply_markup=await MfcKeyboards().choose_fil(mo=mo),
    )
    await state.set_state(MfcStates.choose_fil)



@router.message(
    is_in_filials, StateFilter(MfcStates.choose_fil)
)
async def choose_fil_handler(
    message: Message,
    state: FSMContext,
):
    await state.update_data(fil_=message.text)
    await message.answer(
        text=MfcMessages.main_menu, reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.choose_type_checking)


@router.message(
    F.text.lower() == "начать проверку", StateFilter(MfcStates.choose_type_checking)
)
async def start_checking(
    message: Message, state: FSMContext, check: CheckService = CheckService()
):
    check_data = await state.get_data()
    check_obj = CheckCreate(
        fil_=check_data["fil_"],
        mfc_user_id=check_data["mfc_user_id"],
        is_task=False
    )
    check_in_obj = await check.add_check(check_create=check_obj)
    await state.update_data(check_in_obj.model_dump(mode='json'))
    await message.answer(
        text=MfcMessages.choose_zone_with_time,
        reply_markup=await MfcKeyboards().choose_zone(),
    )
    await state.set_state(MfcStates.choose_zone)


@router.message(
    F.text.lower() == "проверить незавершенные проверки",
    StateFilter(MfcStates.choose_type_checking),
)
async def get_unfinished_checks(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
):
    data = await state.get_data()
    checks = await check_obj.get_mfc_fil_active_checks(fil_=data["fil_"])
    await check_obj.unfinished_checks_process(
        message=message, state=state, checks=checks
    )

@router.callback_query(
    F.data.startswith("delete_unfinished_check_"), MfcStates.choose_type_checking
)
async def delete_unfinished(
    callback: CallbackQuery, state: FSMContext, check_obj: CheckService = CheckService()
):
    check_id = int(callback.data.split("_")[-1])
    result = await check_obj.delete_check_zero_violations(check_id=check_id)
    if result: 
        await callback.answer(
            text=result,
            show_alert=True
        )
    else:    
        await callback.answer(
            text=MfcMessages.check_deleted,
        )
        await state.update_data({
            f'check_unfinished_{check_id}': None
        })
        await callback.message.delete()


@router.callback_query(
    F.data.startswith("finish_unfinished_check_"), MfcStates.choose_type_checking
)
async def finish_unfinished(
    callback: CallbackQuery, state: FSMContext, check_obj: CheckService = CheckService()
):
    check_id = int(callback.data.split("_")[-1])
    await check_obj.finish_unfinished_process(
        state=state, callback=callback, check_id=check_id
    )
    await callback.message.answer(
        text=MfcMessages.choose_zone, reply_markup=await MfcKeyboards().choose_zone()
    )
    await state.set_state(MfcStates.choose_zone)


@router.message(
    F.text.lower() == "добавить уведомление о нарушении",
    StateFilter(MfcStates.choose_type_checking),
)
async def notification_handler(
    message: Message,
    state: FSMContext,
    check: CheckService = CheckService(),
):
    check_data = await state.get_data()
    check_obj = CheckCreate(
        fil_=check_data["fil_"],
        mfc_user_id=check_data["mfc_user_id"],
        is_task=True
    )
    check_in_obj = await check.add_check(check_create=check_obj)
    await message.answer(
        text=MfcMessages.choose_zone, reply_markup=await MfcKeyboards().choose_zone()
    )
    await state.update_data(
        check_in_obj.model_dump(mode='json')
    )
    await state.set_state(MfcStates.choose_zone)


##############
# back_logic #
##############


@router.message(F.text.lower() == "назад")
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcStates.choose_fil:
        await state.clear()
        await message.answer(
            text=MfcMessages.start_message, reply_markup=ReplyKeyboardRemove()
        )
    elif current_state == MfcStates.choose_type_checking:
        data = await state.get_data()
        mo = data["mo"]
        await message.answer(
            text=MfcMessages.welcome_message,
            reply_markup=await MfcKeyboards().choose_fil(mo=mo),
        )
        await state.update_data(
            fil_=None,
            is_task=None,
        )
        await state.set_state(MfcStates.choose_fil)

    elif current_state == MfcStates.choose_zone:
        mo = await UserService().get_user_mo(message.from_user.id)
        await message.answer(
            text=MfcMessages.main_menu,
            reply_markup=MfcKeyboards().main_menu(),
        )
        await state.set_state(MfcStates.choose_type_checking)

    elif current_state == MfcStates.choose_violation:
        await state.set_state(MfcStates.choose_zone)
        await message.answer(
            text=MfcMessages.choose_zone, reply_markup=await MfcKeyboards().choose_zone()
        )
        await state.update_data(zone=None)
    elif current_state == MfcStates.choose_photo_comm:
        await state.set_state(MfcStates.choose_violation)
        data = await state.get_data()
        zone = data["zone"]
        violations_completed = data.get('violations_completed', [])
        await state.update_data(violation_name=None, violation_dict_id=None)
        await message.answer(
            text=MfcMessages.choose_violation(zone=zone),
            reply_markup=await MfcKeyboards().choose_violation(zone=zone, completed_violations=violations_completed),
        )

    elif current_state in (
        MfcStates.add_photo,
        MfcStates.add_comm,
        MfcStates.continue_state,
    ):
        data = await state.get_data()
        violation = data["violation_name"]
        await message.answer(
            text=MfcMessages.add_photo_comm(violation=violation),
            reply_markup=MfcKeyboards().choose_photo_comm(),
        )
        await state.update_data(comm_mfc=None, photo_id_mfc=None)
        await state.set_state(MfcStates.choose_photo_comm)

    else:
        await state.clear()
        await message.answer(text=MfcMessages.start_message)


#######################
# main mfc part logic #
#######################


@router.message(
    is_in_zones, StateFilter(MfcStates.choose_zone)
)
async def choose_zone_handler(message: Message, state: FSMContext):
    zone = ' '.join(message.text.split()[1:])
    data = await state.get_data()
    violations_completed = data.get('violations_completed', [])
    await message.answer(
        text=MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(zone=zone, completed_violations=violations_completed),
    )
    await state.update_data(zone=zone)
    await state.set_state(MfcStates.choose_violation)


@router.message(
    is_in_violations,
    StateFilter(MfcStates.choose_violation),
)
async def choose_violation_handler(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_name = message.text
    if '✅' in violation_name:
        violation_name = message.text.split('✅')[-1].strip()

    data = await state.get_data()
    zone = data["zone"]
    violation_dict_id = await violation_obj.get_dict_id_by_name(
        violation_name=violation_name,
        zone=zone,
    )
    await state.update_data(
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
            text=MfcMessages.violation_already_exist,
            reply_markup=message.reply_markup,
        )
        return
    violation_in_db = await violation_obj.add_violation(violation_create=violation_create_obj)
    violation_out = await violation_obj.form_violation_out(violation=violation_in_db)
    await state.update_data(
        violation_out.model_dump(mode='json')
    )

    await message.answer(
        text=MfcMessages.problem_detection,
        reply_markup=MfcKeyboards().choose_photo_comm(),
    )
    await message.answer(
        text=MfcMessages.add_photo_comm(violation=violation_name),
        reply_markup=MfcKeyboards().get_description(violation_id=violation_dict_id),
    )
    await state.set_state(MfcStates.choose_photo_comm)


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
        text=MfcMessages.choose_zone, reply_markup=await MfcKeyboards().choose_zone()
    )
    await state.update_data(zone=None)


@router.callback_query(F.data.startswith("description_"), ~StateFilter(default_state))
async def get_description(
    callback: CallbackQuery,
    violation_dict_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_id = int(callback.data.split("_")[-1])
    result = await violation_dict_obj.get_description(violation_dict_id=violation_id)
    if result:
        try:
            await callback.answer(text=result, show_alert=True)
        except TelegramBadRequest:
            await callback.message.answer(text=result)
            await callback.answer()
    else:
        await callback.answer(text=MfcMessages.no_description, show_alert=True)


@router.message(
    F.text.lower() == "загрузить фото", StateFilter(MfcStates.choose_photo_comm)
)
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.add_photo, reply_markup=MfcKeyboards().just_cancel()
    )
    await state.set_state(MfcStates.add_photo)


@router.message(
    F.text.lower() == "написать комментарий", StateFilter(MfcStates.choose_photo_comm)
)
async def add_comm_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.add_comm, reply_markup=MfcKeyboards().just_cancel()
    )
    await state.set_state(MfcStates.add_comm)

###############
# add_content #
###############

@router.message(F.photo, StateFilter(MfcStates.add_photo))
async def add_photo_handler_(message: Message, state: FSMContext):
    photo_id_mfc = message.photo[-1].file_id
    data = await state.get_data()
    violation_name = data["violation_name"]
    await state.update_data(photo_id_mfc=photo_id_mfc)
    if data.get("comm_mfc"):
        await message.answer(
            text=MfcMessages.photo_comm_added(violation=violation_name),
            reply_markup=MfcKeyboards().save_or_cancel(),
        )
        await state.set_state(MfcStates.continue_state)
    else:
        await message.answer(
            text=MfcMessages.photo_added, reply_markup=MfcKeyboards().photo_added()
        )
        await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text, not_cancel_filter, not_back_filter, not_buttons_filter, StateFilter(MfcStates.add_comm))
async def add_comm_handler(message: Message, state: FSMContext):
    comm_mfc = message.text
    data = await state.get_data()
    violation_name = data["violation_name"]

    await state.update_data(comm_mfc=comm_mfc)
    if data.get("photo_id_mfc"):
        await message.answer(
            text=MfcMessages.photo_comm_added(violation=violation_name),
            reply_markup=MfcKeyboards().save_or_cancel(),
        )
        await state.set_state(MfcStates.continue_state)
    else:
        await message.answer(
            text=MfcMessages.comm_added, reply_markup=MfcKeyboards().comm_added()
        )
        await state.set_state(MfcStates.choose_photo_comm)


@router.callback_query(F.data == "add_comm_", StateFilter(MfcStates.choose_photo_comm))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MfcMessages.add_comm, reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_comm)
    await callback.answer()


@router.callback_query(F.data == "add_photo_", StateFilter(MfcStates.choose_photo_comm))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MfcMessages.add_photo, reply_markup=MfcKeyboards().just_back()
    )
    await state.set_state(MfcStates.add_photo)
    await callback.answer()


@router.message(
    F.text.lower() == "отменить",
    StateFilter(MfcStates.add_comm, MfcStates.add_photo, MfcStates.continue_state),
)
async def cancel_adding(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    violation = data["violation_name"]
    await message.answer(
        text=MfcMessages.add_photo_comm(violation=violation),
        reply_markup=MfcKeyboards().choose_photo_comm(),
    )
    await state.update_data(comm_mfc=None, photo_id_mfc=None)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text.lower() == "отменить", StateFilter(MfcStates.choose_photo_comm))
async def cancel_adding_vio(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService()
):
    await state.set_state(MfcStates.choose_violation)
    data = await state.get_data()
    zone = data["zone"]
    violations_completed = data.get('violations_completed', [])
    await violation_obj.delete_violation(data['violation_found_id'])
    await state.update_data(
        time_to_correct=None,
        violation_detected=None,
        violation_found_id=None,        
        violation_name=None,
        violation_dict_id=None)
    await message.answer(
        text=MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(zone=zone, completed_violations=violations_completed),
    )

################
# finish_check #
################

@router.callback_query(F.data == "save_and_go", StateFilter(MfcStates.continue_state))
async def save_violation(
    callback: CallbackQuery,
    state: FSMContext,
    violation: ViolationFoundService = ViolationFoundService(),
    check: CheckService = CheckService(),
):
    vio_data = await state.get_data()
    violation_found_obj = ViolationFoundOut(
        **vio_data
        )
    await violation.save_violation_process(
        callback=callback,
        violation_found_out=violation_found_obj,
    )

    await callback.answer(text=MfcMessages.violation_saved, show_alert=True)
    violations_completed = vio_data.get('violations_completed', [])
    violations_completed.append(violation_found_obj.violation_name)
    await state.update_data(violations_completed=violations_completed)

    if vio_data.get("is_task"):
        check_id = vio_data["check_id"]
        check_upd = CheckUpdate(mfc_finish=dt.datetime.now())
        await check.update_check(check_id=check_id, check_update=check_upd)
        await state.clear()
        return

    await callback.message.answer(
        text=MfcMessages.continue_check,
    )
    await callback.message.answer(
        text=MfcMessages.choose_violation(zone=vio_data['zone']),
        reply_markup=await MfcKeyboards().choose_violation(zone=vio_data['zone'], completed_violations=violations_completed),
    )
    await state.update_data(
        {
            'violation_detected': None,
            'time_to_correct': None,
            "violation_found_id": None,
            "violation_name": None,
            "violation_dict_id": None,
            "photo_id_mfc": None,
            "comm_mfc": None,
        }
    )
    await state.set_state(MfcStates.choose_violation)


@router.message(
    F.text.lower() == "⛔️ закончить проверку", StateFilter(MfcStates.choose_zone)
)
async def finish_check(
    message: Message, state: FSMContext, check: CheckService = CheckService()
):
    data = await state.get_data()
    check_id = data.get("check_id")
    violation_count = await check.get_violations_found_count_by_check(check_id=check_id)
    if data['is_task']:
        if violation_count == 0:
            await check.delete_check_zero_violations(check_id=check_id)
            await message.answer(
                text=MfcMessages.finish_task_zero_violations, reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            return
        else:
            await message.answer(
                text=MfcMessages.notification_saved,
                # reply_markup=DefaultKeyboards().get_authorization()
                )
            await state.clear()
            return

    check_upd = CheckUpdate(mfc_finish=dt.datetime.now())
    await check.update_check(check_id=check_id, check_update=check_upd)
    await state.clear()
    await message.answer(
        text=MfcMessages.finish_check, reply_markup=ReplyKeyboardRemove()
    )


# @router.message(Command("start"))
# async def finish_process(message: Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         text=DefaultMessages.start_message,
#         # reply_markup=DefaultKeyboards().get_authorization(),
#     )


@router.message(Command("finish"))
async def finish_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=DefaultMessages.finish,
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message()
async def something_wrong(message: Message):
    await message.answer(text=DefaultMessages.something_wrong)


@router.callback_query(StateFilter(MfcStates))
async def something_wrong(callback: CallbackQuery):
    await callback.answer(text=DefaultMessages.not_good_time)
