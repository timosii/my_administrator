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


@router.message(Command("start"),
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.main_menu(),
        reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.start_checking)


@router.message(F.text.lower() == 'начать проверку',
                StateFilter(MfcStates.start_checking))
async def choose_time_handler(message: Message, state: FSMContext):
    await message.answer(
        text=Messages.choose_time(),
        reply_markup=MfcKeyboards().choose_check_time()
    )
    await state.set_state(MfcStates.choose_time)