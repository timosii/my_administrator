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


# @router.message(
#     F.text.lower() == "проверить нарушения",
#     StateFilter(MoPerformerStates.mo_performer),
# )
# async def are_violations(message: Message,
#                          state: FSMContext,
#                          user: UserService = UserService()):
#     user_id = message.from_user.id
#     mo = await user.get_user_mo(user_id=user_id)

#     await message.answer(
#         text=MoPerformerMessages.choose_fil,
#         reply_markup=await MoPerformerKeyboards().choose_fil(mo=mo),
# )


@router.message(
    lambda message: message.text in get_filials(),
    StateFilter(MoPerformerStates.mo_performer),
)
async def choose_fil_handler(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    fil_ = message.text
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
        )
    else:
        for check in checks:
            text_mes = FormCards().check_card(
                check_fil_=check.fil_,
                check_date=check.mfc_finish,
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
        vio = await violation_obj.get_violation_by_id(violation_id=violation.id)
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
    F.data.startswith("comment_"), StateFilter(MoPerformerStates.mo_performer)
)
async def process_comment_callback(
    callback: CallbackQuery,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_id = int(callback.data.split("_")[1])
    violation = await violation_obj.get_violation_found_by_id(violation_id=violation_id)
    # message = await bot.get_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    text = callback.message.text

    await callback.message.edit_text(
        text=f"{text}\n\nКомментарий для нарушения: {violation.comm}",
        reply_markup=MoPerformerKeyboards().get_under_violation_photo(
            violation_id=violation.id
        ),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("photo_"), StateFilter(MoPerformerStates.mo_performer)
)
async def process_photo_callback(
    callback: CallbackQuery,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    violation_id = int(callback.data.split("_")[1])
    vio = await violation_obj.get_violation_by_id(violation_id=violation_id)
    violation_ = vio.violation_name
    violation_found = await violation_obj.get_violation_found_by_id(
        violation_id=violation_id
    )
    await callback.message.answer_photo(
        photo=violation_found.photo_id,
        caption=f"Фотофиксация нарушения:\n<b>{violation_}</b>",
    )
    await callback.answer()
