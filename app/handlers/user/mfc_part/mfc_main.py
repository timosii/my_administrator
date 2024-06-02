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
from app.filters.default import not_back_filter, not_cancel_filter
from app.database.db_helpers.form_menu import get_zones, get_violations, get_filials
from app.database.services.users import UserService
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.schemas.check_schema import CheckCreate, CheckInDB, CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundCreate,
    ViolationFoundInDB,
    ViolationFoundUpdate,
)
from app.logger_config import Logger
from loguru import logger


router = Router()
router.message.filter(MfcFilter())


@router.message(F.text.lower() == "пройти авторизацию", StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    logger.info(Logger.passed_authorization(message.from_user))
    await message.answer(
        text=MfcMessages.welcome_message, reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.start_checking)


@router.message(
    F.text.lower() == "начать проверку", StateFilter(MfcStates.start_checking)
)
async def choose_fil_handler(
    message: Message, state: FSMContext, user: UserService = UserService()
):
    user_id = message.from_user.id
    mo = await user.get_user_mo(user_id=user_id)
    await state.update_data(user_id=user_id, mo=mo)
    await message.answer(
        text=MfcMessages.choose_fil, reply_markup=await MfcKeyboards().choose_fil(mo=mo)
    )
    await state.set_state(MfcStates.choose_fil)


@router.message(
    F.text.lower() == "проверить незавершенные проверки",
    StateFilter(MfcStates.start_checking),
)
async def choose_fil_handler(
    message: Message,
    state: FSMContext,
    user: UserService = UserService(),
    check_obj: CheckService = CheckService(),
):
    user_id = message.from_user.id
    mo = await user.get_user_mo(user_id=user_id)
    await state.update_data(user_id=user_id, mo=mo)

    checks = await user.get_user_active_checks(user_id=user_id)
    if not checks:
        await message.answer(
            text=MfcMessages.no_unfinished, reply_markup=message.reply_markup
        )
    else:
        for check in checks:
            check_out = await check_obj.form_check_out_unfinished(check=check)
            text_mes = await check_obj.form_check_card_unfinished(check=check_out)
            await state.update_data({
                f'check_unfinished_{check.id}': check.model_dump_json(),
            })
            await message.answer(
                text=text_mes,
                reply_markup=MfcKeyboards().unfinished_check(check_id=check.id),
            )


@router.callback_query(
    F.data.startswith("delete_unfinished_check_"), MfcStates.start_checking
)
async def continue_unfinished(
    callback: CallbackQuery, state: FSMContext, check_obj: CheckService = CheckService()
):
    check_id = int(callback.data.split("_")[-1])
    await check_obj.delete_check(check_id=check_id)
    await callback.message.answer(
        text=MfcMessages.check_deleted,
    )
    await callback.message.delete()


@router.callback_query(
    F.data.startswith("finish_unfinished_check_"), MfcStates.start_checking
)
async def finish_unfinished(callback: CallbackQuery,
                            state: FSMContext,
                            ):
    check_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    check_obj = CheckInDB(**json.loads(data[f"check_unfinished_{check_id}"]))
    
    await state.update_data(
        fil_=check_obj.fil_,
        check_id=check_id,
        )
    await state.update_data({
        f"check_unfinished_{check_id}": None
    })
    await callback.message.answer(
        text=MfcMessages.choose_zone, reply_markup=MfcKeyboards().choose_zone()
    )
    await state.set_state(MfcStates.choose_zone)
    await callback.answer(text='Продолжаем проверку')


@router.message(
    F.text.lower() == "добавить уведомление о нарушении",
    StateFilter(MfcStates.start_checking),
)
async def choose_fil_handler(
    message: Message, state: FSMContext, user: UserService = UserService()
):
    await message.answer(text='Функция находится в разработке, выберите что-нибудь другое')
    # user_id = message.from_user.id
    # mo = await user.get_user_mo(user_id=user_id)
    # await state.update_data(user_id=user_id, mo=mo)
    # await message.answer(
    #     text=MfcMessages.choose_fil, reply_markup=await MfcKeyboards().choose_fil(mo=mo)
    # )
    # await state.set_state(MfcStates.choose_fil)


##############
# back_logic #
##############


@router.message(F.text.lower() == "назад")
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcStates.start_checking:
        await state.clear()
        await message.answer(
            text=MfcMessages.start_message, reply_markup=ReplyKeyboardRemove()
        )
    elif current_state == MfcStates.choose_fil:
        await state.set_state(MfcStates.start_checking)
        await message.answer(
            text=MfcMessages.welcome_message, reply_markup=MfcKeyboards().main_menu()
        )
    elif current_state == MfcStates.choose_zone:
        mo = await UserService().get_user_mo(message.from_user.id)
        await message.answer(
            text=MfcMessages.choose_fil,
            reply_markup=await MfcKeyboards().choose_fil(mo=mo),
        )
        await state.set_state(MfcStates.choose_fil)
    elif current_state == MfcStates.choose_violation:
        await state.set_state(MfcStates.choose_zone)
        await message.answer(
            text=MfcMessages.choose_zone, reply_markup=MfcKeyboards().choose_zone()
        )

    elif current_state == MfcStates.choose_photo_comm:
        await state.set_state(MfcStates.choose_violation)
        data = await state.get_data()
        zone = data["zone"]
        await state.update_data(violation_name=None, vio_id=None)
        await message.answer(
            text=MfcMessages.choose_violation(zone=zone),
            reply_markup=await MfcKeyboards().choose_violation(zone=zone),
        )

    elif current_state in (MfcStates.add_photo, MfcStates.add_comm, MfcStates.continue_state):
        data = await state.get_data()
        violation = data["violation_name"]
        await message.answer(
            text=MfcMessages.add_photo_comm(violation=violation),
            reply_markup=MfcKeyboards().choose_photo_comm(),
        )
        await state.update_data(comm=None, photo_id=None)
        await state.set_state(MfcStates.choose_photo_comm)

    else:
        await state.clear()
        await message.answer(text=MfcMessages.start_message)


#######################
# main mfc part logic #
#######################


@router.message(
    lambda message: message.text in get_filials(), StateFilter(MfcStates.choose_fil)
)
async def choose_fil_handler(
    message: Message, state: FSMContext, check: CheckService = CheckService()
):
    await state.update_data(fil_=message.text)
    check_data = await state.get_data()
    check_obj = CheckCreate(
        fil_=check_data["fil_"],
        user_id=check_data["user_id"],
    )

    check_in_obj = await check.add_check(check_create=check_obj)

    await state.update_data(check_id=check_in_obj.id)
    await message.answer(
        text=MfcMessages.choose_zone, reply_markup=MfcKeyboards().choose_zone()
    )
    await state.set_state(MfcStates.choose_zone)


@router.message(
    lambda message: message.text in get_zones(), StateFilter(MfcStates.choose_zone)
)
async def choose_zone_handler(message: Message, state: FSMContext):
    zone = message.text
    await message.answer(
        text=MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(zone=zone),
    )
    await state.update_data(zone=message.text)
    await state.set_state(MfcStates.choose_violation)


@router.message(
    lambda message: message.text in get_violations(),
    StateFilter(MfcStates.choose_violation),
)
async def choose_violation_handler(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_name = message.text

    data = await state.get_data()
    zone = data["zone"]
    await state.update_data(
        violation_name=violation_name,
        vio_id=await violation_obj.get_id_by_name(
            zone=zone, violation_name=violation_name
        ),
    )
    check_id = data["check_id"]
    data_ = await state.get_data()
    violation_dict_id = data_["vio_id"]

    is_vio_already_in_check = await violation_obj.is_vio_already_in_check(
        violation_dict_id=violation_dict_id,
        check_id=check_id,
    )
    if is_vio_already_in_check:
        await message.answer(
            text=MfcMessages.violation_already_exist, reply_markup=message.reply_markup
        )
        return

    await message.answer(
        text=MfcMessages.add_photo_comm(violation=violation_name),
        reply_markup=MfcKeyboards().choose_photo_comm(),
    )

    await state.set_state(MfcStates.choose_photo_comm)


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
async def add_photo_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.add_comm, reply_markup=MfcKeyboards().just_cancel()
    )
    await state.set_state(MfcStates.add_comm)


###############
# add_content #
###############


@router.message(F.photo, StateFilter(MfcStates.add_photo))
async def add_photo_handler(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    violation_name = data["violation_name"]
    await state.update_data(photo_id=photo_id)
    if data.get("comm"):
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


@router.message(F.text, not_cancel_filter, StateFilter(MfcStates.add_comm))
async def add_comm_handler(message: Message, state: FSMContext):
    comm = message.text
    data = await state.get_data()
    violation_name = data["violation_name"]

    await state.update_data(comm=comm)
    if data.get("photo_id"):
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
    await state.update_data(comm=None, photo_id=None)
    await state.set_state(MfcStates.choose_photo_comm)


@router.message(F.text.lower() == "отменить", StateFilter(MfcStates.choose_photo_comm))
async def cancel_adding_vio(
    message: Message,
    state: FSMContext,
):
    await state.set_state(MfcStates.choose_violation)
    data = await state.get_data()
    zone = data["zone"]
    await state.update_data(violation_name=None)
    await message.answer(
        text=MfcMessages.choose_violation(zone=zone),
        reply_markup=await MfcKeyboards().choose_violation(zone=zone),
    )


################
# finish_check #
################


@router.callback_query(F.data == "save_and_go", StateFilter(MfcStates.continue_state))
async def save_violation(
    callback: CallbackQuery,
    state: FSMContext,
    violation: ViolationFoundService = ViolationFoundService(),
):
    vio_data = await state.get_data()
    violation_name = vio_data["violation_name"]
    await callback.message.edit_text(
        text=MfcMessages.save_violation(violation=violation_name), reply_markup=None
    )
    vio_obj = ViolationFoundCreate(
        check_id=vio_data["check_id"],
        violation_id=vio_data["vio_id"],
        photo_id=vio_data["photo_id"],
        comm=vio_data["comm"],
    )
    await violation.add_violation(violation_create=vio_obj)
    await callback.answer(text="Информация о нарушении сохранена!", show_alert=True)
    await state.update_data(
        {
            "zone": None,
            "violation_name": None,
            "vio_id": None,
            "photo_id": None,
            "comm": None,
        }
    )
    await callback.message.answer(
        text=MfcMessages.continue_check,
    )
    await callback.message.answer(
        text=MfcMessages.choose_zone, reply_markup=MfcKeyboards().choose_zone()
    )

    await state.set_state(MfcStates.choose_zone)


@router.message(
    F.text.lower() == "закончить проверку", StateFilter(MfcStates.choose_zone)
)
async def finish_check(
    message: Message, state: FSMContext, check: CheckService = CheckService()
):
    data = await state.get_data()
    check_id = data["check_id"]
    check_upd = CheckUpdate(mfc_finish=dt.datetime.now())
    await check.update_check(check_id=check_id, check_update=check_upd)
    await state.clear()
    await message.answer(
        text=MfcMessages.finish_check, reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("start"))
async def finish_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=DefaultMessages.start_message,
        reply_markup=DefaultKeyboards().get_authorization(),
    )


@router.message(Command("finish"))
async def finish_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=DefaultMessages.finish,
        reply_markup=ReplyKeyboardRemove(),
    )




@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await message.answer(text=DefaultMessages.something_wrong)
