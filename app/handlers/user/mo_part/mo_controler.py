from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.mo_part import MoControlerKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import MoControlerMessages, DefaultMessages
from app.handlers.states import MoControlerStates
from app.filters.mo_filters import MoControlerFilter

router = Router() 
router.message.filter(MoControlerFilter())


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=MoControlerMessages.start_message,
        reply_markup=MoControlerKeyboards().main_menu()
    )
    await state.set_state(MoControlerStates.mo_controler)

@router.message(F.text.lower() == "назад", StateFilter(MoControlerStates.mo_controler))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            text=DefaultMessages.start_message,
        )
