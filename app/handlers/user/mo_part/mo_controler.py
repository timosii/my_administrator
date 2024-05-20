from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoControlerKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import MoControlerMessages
from app.data import ZONES, TIME_POINTS, CHOOSE
from app.handlers.states import MoControlerStates
from app.filters.mo_filters import MoControlerFilter

router = Router() 
router.message.filter(MoControlerFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MoControlerMessages.start_message,
        reply_markup=MoControlerKeyboards().main_menu()
    )
    await state.set_state(MoControlerStates.mo_controler)
