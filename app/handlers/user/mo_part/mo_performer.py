from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoPerformerKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import MoPerformerMessages
from app.handlers.states import MoPerformerStates
from app.filters.mo_filters import MoPerformerFilter

router = Router() 
router.message.filter(MoPerformerFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MoPerformerMessages.start_message,
        reply_markup=MoPerformerKeyboards().main_menu()
    )
    await state.set_state(MoPerformerStates.mo_performer)
