from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import MfcMessages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.states import MfcStates
from app.filters.mfc_filters import MfcFilter

router = Router() 
router.message.filter(MfcFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.welcome_message,
        reply_markup=MfcKeyboards().main_menu()
    )
    await state.set_state(MfcStates.start_checking)

@router.message(F.text.lower() == 'начать проверку',
                StateFilter(MfcStates.start_checking))
async def choose_time_handler(message: Message, state: FSMContext):
    await message.answer(
        text=MfcMessages.choose_time,
        reply_markup=MfcKeyboards().choose_check_time()
    )
    await state.set_state(MfcStates.choose_time)