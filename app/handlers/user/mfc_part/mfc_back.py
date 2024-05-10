from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import Messages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.user.states import MfcStates

router = Router() 


@router.message(F.text.lower() == 'назад')
async def back_command(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == MfcStates.choose_time:
        await state.set_state(default_state)
        await message.answer(
            text=Messages.main_menu(),
        )
    elif current_state == MfcStates.choose_zone:
        await state.set_state(MfcStates.choose_time)
        await message.answer(
            text=Messages.choose_time(),
            reply_markup=MfcKeyboards().choose_check_time()
        )
    elif current_state == MfcStates.choose_violation:
        await state.set_state(MfcStates.choose_zone)
        await message.answer(
            text=Messages.choose_zone(),
            reply_markup=MfcKeyboards().choose_zone()
        )
    elif current_state == MfcStates.choose_photo_comm:
        await state.set_state(MfcStates.choose_violation)
        data = await state.get_data()
        zone = data['zone']
        await message.answer(
            text=Messages.choose_violation(zone=zone),
            reply_markup=MfcKeyboards().choose_violation(zone=zone)
        )
    elif current_state in (
        MfcStates.add_comm,
        MfcStates.add_photo
    ):
        await state.set_state(MfcStates.choose_photo_comm)
        data = await state.get_data()
        violation = data['violation']
        await message.answer(
            text=Messages.add_photo_comm(violation=violation),
            reply_markup=MfcKeyboards().choose_photo_comm()
        )
    else:
        await state.clear()
        await message.answer(
            text=Messages.start_message()
        )
        