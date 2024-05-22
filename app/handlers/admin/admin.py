from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.admin import AdminKeyboards
from app.keyboards.default import DefaultKeyboards
from app.handlers.messages import AdminMessages, DefaultMessages
from app.handlers.states import AdminStates
from app.filters.admin import AdminFilter

router = Router() 
router.message.filter(AdminFilter())


@router.message(F.text.lower() == 'пройти авторизацию',
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=AdminMessages.start_message,
        reply_markup=AdminKeyboards().main_menu()
    )
    await state.set_state(AdminStates.admin)

@router.message(F.text.lower() == "назад", StateFilter(AdminStates.admin))
async def back_command(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
            text=DefaultMessages.start_message,
            reply_markup=DefaultKeyboards().get_authorization()
        )
