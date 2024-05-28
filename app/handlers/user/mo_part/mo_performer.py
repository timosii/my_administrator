import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoPerformerKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MoPerformerMessages, DefaultMessages
from app.handlers.states import MoPerformerStates
from app.filters.mo_filters import MoPerformerFilter
from app.database.db_helpers.form_menu import get_zones, get_violations, get_filials
from app.database.services.check import CheckService
from app.database.services.violations_found import ViolationFoundService
from app.database.services.users import UserService
from app.view.cards import FormCards

from aiogram import Bot

router = Router()
router.message.filter(MoPerformerFilter())


@router.message(F.text.lower() == "пройти авторизацию", StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.start_message,
        reply_markup=MoPerformerKeyboards().main_menu(),
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.message(F.text.lower() == "назад", StateFilter(MoPerformerStates.mo_performer))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=DefaultMessages.start_message,
        reply_markup=DefaultKeyboards().get_authorization(),
    )


@router.message(
    F.text.lower() == "посмотреть активные проверки",
    StateFilter(MoPerformerStates.mo_performer),
)
async def are_violations(
    message: Message, state: FSMContext, user: UserService = UserService()
):
    user_id = message.from_user.id
    mo = await user.get_user_mo(user_id=user_id)

    await message.answer(
        text=MoPerformerMessages.choose_fil,
        reply_markup=await MoPerformerKeyboards().choose_fil(mo=mo),
    )


@router.message(
    lambda message: message.text in get_filials(),
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_checks(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    fil_ = message.text
    await state.update_data(fil_=fil_)
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
        )
    else:
        for check in checks:
            text_mes = FormCards().check_card(
                check_fil_=check.fil_,
                check_start=check.mfc_start,
                check_finish=check.mfc_finish,
                violations_count=len(
                    await violation_obj.get_violations_found_by_check(check_id=check.id)
                ),
            )
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.id)

            await message.answer(text=text_mes, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith("violations_"), StateFilter(MoPerformerStates.mo_performer)
)
async def get_violations(
    callback: CallbackQuery,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    check_id = int(callback.data.split("_")[1])
    violations = await violation_obj.get_violations_found_by_check(check_id=check_id)

    for violation in violations:
        vio = await violation_obj.get_violation_by_id(
            violation_id=violation.violation_id
        )
        zone = vio.zone
        violation_name = vio.violation_name
        vio_duration = vio.time_to_correct
        keyboard = MoPerformerKeyboards().get_under_violation_photo(
            violation_id=violation.id
        )
        text_mes = FormCards().violation_card(
            violation_zone=zone,
            violation_name=violation_name,
            violation_detected=violation.violation_detected,
            violation_comm=violation.comm,
            violation_duration=vio_duration,
        )

        await callback.message.answer(text=text_mes, reply_markup=keyboard)

    await callback.answer()


@router.callback_query(
    F.data.startswith("photo_"), StateFilter(MoPerformerStates.mo_performer)
)
async def process_photo_callback(
    callback: CallbackQuery,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    vio_id = int(callback.data.split("_")[1])
    violation_found_obj = await violation_obj.get_violation_found_by_id(
        violation_id=vio_id
    )
    vio_dict_id = violation_found_obj.violation_id
    vio_dict_obj = await violation_obj.get_violation_by_id(violation_id=vio_dict_id)
    violation = vio_dict_obj.violation_name
    zone = vio_dict_obj.zone
    text_mes = FormCards().violation_card(
        violation_zone=zone,
        violation_name=violation,
        violation_detected=violation_found_obj.violation_detected,
        violation_comm=violation_found_obj.comm,
        violation_duration=vio_dict_obj.time_to_correct,
    )
    await callback.message.answer_photo(
        photo=violation_found_obj.photo_id,
        caption=f"Фотофиксация нарушения:\n{text_mes}",
        reply_markup=MoPerformerKeyboards.vio_correct_with_photo(violation_id=vio_id)
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("correct_"), StateFilter(MoPerformerStates.mo_performer)
)
async def process_correct_callback(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    vio_id = int(callback.data.split("_")[1])
    await state.update_data(vio_id=vio_id)
    violation_found_obj = await violation_obj.get_violation_found_by_id(
        violation_id=vio_id
    )
    vio_dict_id = violation_found_obj.violation_id
    vio_dict_obj = await violation_obj.get_violation_by_id(violation_id=vio_dict_id)
    violation = vio_dict_obj.violation_name
    zone = vio_dict_obj.zone
    text_mes = FormCards().violation_card(
        violation_zone=zone,
        violation_name=violation,
        violation_detected=violation_found_obj.violation_detected,
        violation_comm=violation_found_obj.comm,
        violation_duration=vio_dict_obj.time_to_correct,
    )

    await callback.message.answer(
        text=f"Вы в режиме исправления нарушения:\n{text_mes}\nВы можете добавить информацию.",
        reply_markup=MoPerformerKeyboards().correct_violation(),
    )
    await callback.answer()
    await state.set_state(MoPerformerStates.correct_violation)


@router.message(
    F.text.lower() == "написать комментарий",
    StateFilter(MoPerformerStates.correct_violation),
)
async def correct_vio_process(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.add_comm,
        # reply_markup=().just_back()
    )
    await state.set_state(MoPerformerStates.add_comm)


@router.message(
    F.text.lower() == "загрузить фото", StateFilter(MoPerformerStates.correct_violation)
)
async def correct_vio_process_photo(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.add_photo,
        # reply_markup=MoPerformerKeyboards.add_photo()
    )
    await state.set_state(MoPerformerStates.add_photo)


@router.message(F.photo,
                StateFilter(MoPerformerStates.add_photo))
async def add_photo_handler(message: Message,
                            state: FSMContext):
    data = await state.get_data()
    violation_id = data['vio_id']
    photo_id = message.photo[-1].file_id
    await state.update_data(
        photo_id=photo_id
    )

    await message.answer(
        text=MoPerformerMessages.photo_added,
        reply_markup=MoPerformerKeyboards.add_photo(violation_id=violation_id)
    )
    await state.set_state(MoPerformerStates.correct_violation)

@router.message(F.text,
                StateFilter(MoPerformerStates.add_comm))
async def add_photo_handler(message: Message,
                            state: FSMContext):
    data = await state.get_data()
    violation_id = data['vio_id']
    comm = message.text
    await state.update_data(
        comm=comm
    )

    await message.answer(
        text=MoPerformerMessages.comm_added,
        reply_markup=MoPerformerKeyboards.add_comm(violation_id=violation_id)
    )
    await state.set_state(MoPerformerStates.correct_violation)

@router.callback_query(F.data.startswith("comm_after_photo_"),
                       StateFilter(MoPerformerStates.correct_violation))

async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MoPerformerMessages.add_comm,
    )
    await state.set_state(MoPerformerStates.continue_check)
    await callback.answer()


@router.callback_query(F.data.startswith("photo_after_comm_"),
                       StateFilter(MoPerformerStates.correct_violation))
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MoPerformerMessages.add_photo,
    )
    await state.set_state(MoPerformerStates.continue_check)
    await callback.answer()

@router.message(
    F.text.lower() == "вернуться к проверке",
    StateFilter(MoPerformerStates.correct_violation,
                MoPerformerStates.add_comm,
                MoPerformerStates.add_photo,
                MoPerformerStates.mo_performer),
)
async def correct_vio_process_back(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    await state.update_data(vio_id=None)
    await state.set_state(MoPerformerStates.mo_performer)

    data = await state.get_data()
    fil_ = data["fil_"]
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
        )
    else:
        for check in checks:
            text_mes = FormCards().check_card(
                check_fil_=check.fil_,
                check_start=check.mfc_start,
                check_finish=check.mfc_finish,
                violations_count=len(
                    await violation_obj.get_violations_found_by_check(check_id=check.id)
                ),
            )
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.id)

            await message.answer(text=text_mes, reply_markup=keyboard)


@router.message(F.photo | F.text,
                StateFilter(MoPerformerStates.continue_check))
async def add_photo_comm_after(message: Message, state: FSMContext):
    data = await state.get_data()
    vio_id = data['vio_id']
    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(
            photo_id=photo_id
        )
    else:
        comm = message.text
        await state.update_data(
            comm=comm
        )

    await message.answer(
        text=MoPerformerMessages.photo_comm_added(vio_id=vio_id),
        reply_markup=MoPerformerKeyboards().back_to_check()
    )
    await state.set_state(MoPerformerStates.mo_performer)





# @router.message(F.text.lower() == 'загрузить фото',
#                 StateFilter(MfcStates.choose_photo_comm))
# async def add_photo_handler(message: Message, state: FSMContext):
#     await message.answer(
#         text=MfcMessages.add_photo,
#         reply_markup=MfcKeyboards().just_back()
#     )
#     await state.set_state(MfcStates.add_photo)


# @router.message(F.text.lower() == 'написать комментарий',
#                 StateFilter(MfcStates.choose_photo_comm))
# async def add_photo_handler(message: Message, state: FSMContext):
#     await message.answer(
#         text=MfcMessages.add_comm,
#         reply_markup=MfcKeyboards().just_back()
#     )
#     await state.set_state(MfcStates.add_comm)

# ###############
# # add_content #
# ###############

# @router.message(F.photo,
#                 StateFilter(MfcStates.add_photo))
# async def add_photo_handler(message: Message,
#                             state: FSMContext):
#     photo_id = message.photo[-1].file_id
#     await state.update_data(
#         photo_id=photo_id
#     )

#     await message.answer(
#         text=MfcMessages.photo_added,
#         reply_markup=MfcKeyboards().photo_added()
#     )
#     await state.set_state(MfcStates.continue_state)

# @router.callback_query(F.data == "add_comm_",
#                        StateFilter(MfcStates.continue_state))
# async def start_check(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer(
#         text=MfcMessages.add_comm,
#         reply_markup=MfcKeyboards().just_back()
#     )
#     await callback.answer()

# @router.message(F.text,
#                 StateFilter(MfcStates.add_comm))
# async def add_comm_handler(message: Message,
#                            state: FSMContext):
#     comm = message.text
#     await state.update_data(
#         comm=comm
#     )
#     await message.answer(
#         text=MfcMessages.comm_added,
#         reply_markup=MfcKeyboards().comm_added()
#     )
#     await state.set_state(MfcStates.continue_state) 

# @router.callback_query(F.data == "add_photo_",
#                        StateFilter(MfcStates.continue_state))
# async def start_check(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer(
#         text=MfcMessages.add_photo,
#         reply_markup=MfcKeyboards().just_back()
#     )
#     await callback.answer()

# @router.message(F.photo | F.text,
#                 StateFilter(MfcStates.continue_state))
# async def add_photo_comm_after(message: Message, state: FSMContext):
#     data = await state.get_data()
#     violation_name = data['violation_name']
#     if message.photo:
#         photo_id = message.photo[-1].file_id
#         await state.update_data(
#             photo_id=photo_id
#         )
#     else:
#         comm = message.text
#         await state.update_data(
#             comm=comm
#         )

#     await message.answer(
#         text=MfcMessages.photo_comm_added(violation=violation_name),
#         reply_markup=MfcKeyboards().save_or_cancel()
#     )