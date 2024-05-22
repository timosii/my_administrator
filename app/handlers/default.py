import time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.default import DefaultKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import DefaultMessages
from app.handlers.states import MfcStates
from app.filters.mfc_filters import MfcFilter


router = Router() 

@router.message(Command("start"),
                StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=DefaultMessages.start_message,
        reply_markup=DefaultKeyboards().get_authorization()
    )


@router.message(Command("hard_reset"),
                StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text='Чиним всё ...',
    )
    time.sleep(2)
    await state.clear()

    await message.answer(
        text='Готово! Вы можете авторизоваться',
        reply_markup=DefaultKeyboards().get_authorization()
    )


@router.message(Command("check_state"),
                StateFilter('*'))
async def cmd_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Вы находитесь в состоянии: {current_state}")
