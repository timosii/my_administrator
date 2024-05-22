from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mfc_part import MfcLeaderKeyboards
from app.handlers.messages import MfcLeaderMessages
from app.handlers.states import MfcLeaderStates
from app.filters.mfc_filters import MfcLeaderFilter

router = Router() 
router.message.filter(MfcLeaderFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MfcLeaderMessages.start_message,
        reply_markup=MfcLeaderKeyboards().main_menu()
    )
    await state.set_state(MfcLeaderStates.mfc_leader)
