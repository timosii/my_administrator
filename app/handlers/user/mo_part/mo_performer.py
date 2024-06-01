import time
import asyncio
import json
import datetime as dt
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
from app.database.schemas.check_schema import CheckOut, CheckUpdate
from app.database.schemas.violation_found_schema import (
    ViolationFoundOut,
    ViolationFoundUpdate,
)
from app.utils.utils import get_index_by_violation_id

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
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)

    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
            reply_markup=message.reply_markup,
        )
    else:
        await state.update_data(fil_=fil_, mo_user_id=message.from_user.id)
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
    await state.update_data(current_check_id=check_id)
    violations = await violation_obj.get_violations_found_by_check(check_id=check_id)
    data = await state.get_data()
    if not data.get("mo_start"):
        await state.update_data(mo_start=dt.datetime.now().isoformat())

    if not violations:
        await callback.message.answer(
            text=MoPerformerMessages.no_violations,
            reply_markup=MoPerformerKeyboards().check_finished(),
        )

    else:
        await state.update_data(violations_out=None)
        violations_out = dict()
        for violation in violations:
            violation_out = await violation_obj.form_violation_out(violation=violation)
            violations_out[f"vio_{violation_out.id}"] = violation_out.model_dump_json()
        await state.update_data(violations_out=violations_out)
        violations_out.clear()
        data = await state.get_data()
        violation_out_objects = sorted(
            [
                ViolationFoundOut(**json.loads(v))
                for _, v in data["violations_out"].items()
            ],
            key=lambda x: x.violation_id,
        )

        reply_obj = FormCards().form_reply(
            violations_out=violation_out_objects, order=0
        )
        photo_id = reply_obj.photo_id
        text_mes = reply_obj.text_mes
        keyboard = reply_obj.keyboard
        await callback.message.answer_photo(
            photo=photo_id, caption=text_mes, reply_markup=keyboard
        )
        await callback.answer()


@router.callback_query(
    F.data.startswith("next_") | F.data.startswith("prev_"),
    StateFilter(MoPerformerStates.mo_performer),
)
async def get_violations(
    callback: CallbackQuery,
    state: FSMContext,
):
    violation_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    violation_out_objects = sorted(
        [ViolationFoundOut(**json.loads(v)) for _, v in data["violations_out"].items()],
        key=lambda x: x.violation_id,
    )

    order = get_index_by_violation_id(
        objects=violation_out_objects, violation_id=violation_id
    )
    print(order)
    reply_obj = FormCards().form_reply(
        violations_out=violation_out_objects, order=order
    )
    if not reply_obj:
        await callback.answer(text=MoPerformerMessages.no_violations)
        return
    photo_id = reply_obj.photo_id
    text_mes = reply_obj.text_mes
    keyboard = reply_obj.keyboard
    await callback.message.answer_photo(
        photo=photo_id, caption=text_mes, reply_markup=keyboard
    )
    await callback.message.delete()
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
    violation_out = ViolationFoundOut(
        **json.loads(data["violations_out"][f"vio_{vio_id}"])
    )
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
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(MoPerformerStates.add_comm)


@router.message(
    F.text.lower() == "загрузить фото", StateFilter(MoPerformerStates.correct_violation)
)
async def correct_vio_process_photo(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.add_photo,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(MoPerformerStates.add_photo)


@router.message(F.photo, StateFilter(MoPerformerStates.add_photo))
async def add_photo_handler(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    data = await state.get_data()
    violation_id = data["current_vio_id"]
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)

    if data.get("comm"):
        await message.answer(
            text=MoPerformerMessages.photo_comm_added(vio_id=violation_id),
            reply_markup=MoPerformerKeyboards().back_to_violations(),
        )
        comm = data["comm"]
        vio_upd = ViolationFoundUpdate(
            photo_id_mo=photo_id, comm_mo=comm, violation_fixed=dt.datetime.now()
        )
        await violation_obj.update_violation(
            violation_id=violation_id, violation_update=vio_upd
        )

        await state.update_data(
            {
                "current_vio_id": None,
                "photo_id": None,
                "comm": None,
                f"vio_{violation_id}": None,
            }
        )
        await state.set_state(MoPerformerStates.mo_performer)

    else:
        await message.answer(
            text=MoPerformerMessages.photo_added,
            reply_markup=MoPerformerKeyboards.add_photo(violation_id=violation_id),
        )
        await state.set_state(MoPerformerStates.correct_violation)


@router.message(F.text, StateFilter(MoPerformerStates.add_comm))
async def add_photo_handler(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    data = await state.get_data()
    violation_id = data["current_vio_id"]
    comm = message.text
    await state.update_data(comm=comm)

    if data.get("photo_id"):
        await message.answer(
            text=MoPerformerMessages.photo_comm_added(vio_id=violation_id),
            reply_markup=MoPerformerKeyboards().back_to_violations(),
        )
        photo_id = data["photo_id"]
        vio_upd = ViolationFoundUpdate(
            photo_id_mo=photo_id, comm_mo=comm, violation_fixed=dt.datetime.now()
        )
        await violation_obj.update_violation(
            violation_id=violation_id, violation_update=vio_upd
        )

        await state.update_data(
            {
                "current_vio_id": None,
                "photo_id": None,
                "comm": None,
                f"vio_{violation_id}": None,
            }
        )
        await state.set_state(MoPerformerStates.mo_performer)

    else:
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
    await state.set_state(MoPerformerStates.add_comm)
    await callback.answer()


@router.callback_query(
    F.data.startswith("photo_after_comm_"),
    StateFilter(MoPerformerStates.correct_violation),
)
async def photo_after_comm(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text=MoPerformerMessages.add_photo,
    )
    await state.set_state(MoPerformerStates.add_photo)
    await callback.answer()


@router.message(
    F.text.lower() == "продолжить проверку",
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_continue(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    data = await state.get_data()
    check_id = data["current_check_id"]
    violations = await violation_obj.get_violations_found_by_check(check_id=check_id)
    await message.answer(
        text=MoPerformerMessages.continue_check, reply_markup=ReplyKeyboardRemove()
    )
    time.sleep(2)

    if not violations:
        await message.answer(
            text=MoPerformerMessages.no_violations,
            reply_markup=MoPerformerKeyboards().check_finished(),
        )

    else:
        for violation in violations:
            violation_out = await violation_obj.form_violation_out(violation=violation)
            await state.update_data(
                {f"vio_{violation_out.id}": violation_out.model_dump_json()}
            )
            text_mes = await violation_obj.form_violation_card(violation=violation_out)
            keyboard = MoPerformerKeyboards().get_under_violation_photo(
                violation_id=violation.id
            )
            await message.answer(text=text_mes, reply_markup=keyboard)


@router.message(
    F.text.lower() == "закончить проверку",
    StateFilter(MoPerformerStates.mo_performer),
)
async def correct_vio_process_finish(
    message: Message,
    state: FSMContext,
    check_obj: CheckService = CheckService(),
    violation_found_obj: ViolationFoundService = ViolationFoundService(),
):
    data = await state.get_data()
    check_id = data["current_check_id"]
    violations_check_count = (
        await violation_found_obj.get_violations_found_count_by_check(check_id=check_id)
    )
    if violations_check_count != 0:
        await message.answer(
            text=MoPerformerMessages.cant_finish, reply_markup=message.reply_markup
        )
        return

    check_upd = CheckUpdate(
        mo_user_id=data["mo_user_id"],
        mo_start=dt.datetime.fromisoformat(data["mo_start"]),
        mo_finish=dt.datetime.now(),
    )

    await check_obj.update_check(check_id=check_id, check_update=check_upd)
    await state.update_data(mo_start=None)
    fil_ = data["fil_"]
    checks = await check_obj.get_all_active_checks_by_fil(fil_=fil_)
    await message.answer(text=MoPerformerMessages.back_to_checks)
    if not checks:
        await message.answer(
            text=MoPerformerMessages.form_no_checks_answer(fil_=fil_),
        )
        await state.clear()
        await message.answer(
            text=DefaultMessages.finish,
            reply_markup=ReplyKeyboardRemove(),
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


##############
# back_logic #
##############


@router.message(F.text.lower() == "назад")
async def back_command(
    message: Message,
    state: FSMContext,
    violation_obj: ViolationFoundService = ViolationFoundService(),
):
    current_state = await state.get_state()
    if current_state == MoPerformerStates.mo_performer:
        await state.clear()
        await message.answer(
            text=MoPerformerMessages.start_message,
            reply_markup=MoPerformerKeyboards().main_menu(),
        )

    elif current_state == MoPerformerStates.correct_violation:
        await message.answer(
            text=MoPerformerMessages.choose_vio, reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(MoPerformerStates.mo_performer)
        data = await state.get_data()
        violations = [
            ViolationFoundOut(**json.loads(v))
            for k, v in data.items()
            if (k.startswith("vio_") and v)
        ]

        for violation in violations:
            text_mes = await violation_obj.form_violation_card(violation=violation)
            keyboard = MoPerformerKeyboards().get_under_violation_photo(
                violation_id=violation.id
            )
            await message.answer(text=text_mes, reply_markup=keyboard)

    else:
        await state.clear()
        await message.answer(text=MoPerformerStates.mo_performer)


@router.message()
async def something_wrong(message: Message, state: FSMContext):
    await message.answer(text=DefaultMessages.something_wrong)
