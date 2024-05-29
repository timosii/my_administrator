import asyncio
import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto
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
from app.database.schemas.check_schema import CheckOut
from app.database.schemas.violation_found_schema import ViolationFoundOut

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
            check_out = await check_obj.form_check_out(check=check)
            await state.update_data(
                {f"check_{check_out.id}": check_out.model_dump_json()}
            )
            text_mes = await check_obj.form_check_card(check=check_out)
            keyboard = MoPerformerKeyboards().get_under_check(check_id=check.id)
            await message.answer(text=text_mes, reply_markup=keyboard)


@router.callback_query(
    F.data.startswith("violations_"), StateFilter(MoPerformerStates.mo_performer)
)
async def get_violations(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    check_id = int(callback.data.split("_")[1])
    violations = await violation_obj.get_violations_found_by_check(check_id=check_id)

    for violation in violations:
        violation_out = await violation_obj.form_violation_out(violation=violation)
        await state.update_data(
            {f"vio_{violation_out.id}": violation_out.model_dump_json()}
        )
        text_mes = await violation_obj.form_violation_card(violation=violation_out)
        keyboard = MoPerformerKeyboards().get_under_violation_photo(
            violation_id=violation.id
        )
        await callback.message.answer(text=text_mes, reply_markup=keyboard)

    await callback.answer()


@router.callback_query(
    F.data.startswith("photo_"), StateFilter(MoPerformerStates.mo_performer)
)
async def process_photo_callback(
    callback: CallbackQuery,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    vio_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    violation_out = ViolationFoundOut(**json.loads(data[f"vio_{vio_id}"]))
    text_mes = await violation_obj.form_violation_card(violation=violation_out)

    await callback.message.answer_photo(
        photo=violation_out.photo_id,
        caption=f"Фотофиксация нарушения:\n{text_mes}",
        reply_markup=MoPerformerKeyboards.vio_correct_with_photo(violation_id=vio_id),
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
    await state.update_data(current_vio_id=vio_id)
    data = await state.get_data()
    violation_out = ViolationFoundOut(**json.loads(data[f"vio_{vio_id}"]))
    text_mes = await violation_obj.form_violation_card(violation=violation_out)

    await callback.message.answer(
        text=MoPerformerMessages.correct_mode(text_mes=text_mes),
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
        reply_markup=MoPerformerKeyboards().back_to_check(),
    )
    await state.set_state(MoPerformerStates.add_comm)


@router.message(
    F.text.lower() == "загрузить фото", StateFilter(MoPerformerStates.correct_violation)
)
async def correct_vio_process_photo(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.add_photo,
        reply_markup=MoPerformerKeyboards().back_to_check(),
    )
    await state.set_state(MoPerformerStates.add_photo)


@router.message(F.photo, StateFilter(MoPerformerStates.add_photo))
async def add_photo_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    violation_id = data["current_vio_id"]
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)

    await message.answer(
        text=MoPerformerMessages.photo_added,
        reply_markup=MoPerformerKeyboards.add_photo(violation_id=violation_id),
    )
    await state.set_state(MoPerformerStates.correct_violation)


@router.message(lambda mes: mes.text and (mes.text.lower() != 'вернуться к выбору проверки'),
                StateFilter(MoPerformerStates.add_comm))
async def add_photo_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    violation_id = data["current_vio_id"]
    comm = message.text
    await state.update_data(comm=comm)

    await message.answer(
        text=MoPerformerMessages.comm_added,
        reply_markup=MoPerformerKeyboards.add_comm(violation_id=violation_id),
    )
    await state.set_state(MoPerformerStates.correct_violation)


@router.callback_query(
    F.data.startswith("comm_after_photo_"),
    StateFilter(MoPerformerStates.correct_violation),
)
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MoPerformerMessages.add_comm,
    )
    await state.set_state(MoPerformerStates.continue_check)
    await callback.answer()


@router.message(lambda c: c.photo or (c.text and c.text.lower() != 'вернуться к выбору проверки'),
                StateFilter(MoPerformerStates.continue_check))
async def add_photo_comm_after(message: Message, state: FSMContext):
    data = await state.get_data()
    vio_id = data["current_vio_id"]
    if message.photo:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    else:
        comm = message.text
        await state.update_data(comm=comm)

    await message.answer(
        text=MoPerformerMessages.photo_comm_added(vio_id=vio_id),
        reply_markup=MoPerformerKeyboards().back_to_check(),
    )
    await state.set_state(MoPerformerStates.mo_performer)


@router.callback_query(
    F.data.startswith("photo_after_comm_"),
    StateFilter(MoPerformerStates.correct_violation),
)
async def start_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MoPerformerMessages.add_photo,
    )
    await state.set_state(MoPerformerStates.continue_check)
    await callback.answer()


@router.message(
    F.text.lower() == "выбрать другое нарушение",
    StateFilter(
        MoPerformerStates.correct_violation,
        MoPerformerStates.add_comm,
        MoPerformerStates.add_photo,
        MoPerformerStates.mo_performer,
    ),
)
async def correct_vio_process_back(
    message: Message,
    state: FSMContext,
):
    await state.update_data(current_vio_id=None, photo_id=None, comm=None)
    await state.set_state(MoPerformerStates.mo_performer)

    await message.answer(
        text=MoPerformerMessages.choose_another,
        reply_markup=MoPerformerKeyboards.get_under_check(),
    )


@router.message(
    F.text.lower() == "вернуться к выбору проверки",
    StateFilter(
        ~StateFilter(default_state)
    ),
)
async def correct_vio_process_back_to_check(
    message: Message, state: FSMContext, check_obj: CheckService = CheckService()
):
    data = await state.get_data()
    checks = [
        CheckOut(**json.loads(v)) for k, v in data.items() if k.startswith("check_")
    ]
    for check in checks:
        text_mes = await check_obj.form_check_card(check=check)
        keyboard = MoPerformerKeyboards().get_under_check(check_id=check.id)
        await message.answer(text=text_mes, reply_markup=keyboard)
