import time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.default import DefaultKeyboards
from app.keyboards.default import DevKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import DefaultMessages
from app.handlers.states import MfcStates
from app.filters.mfc_filters import MfcFilter


router = Router() 


@router.message(Command("dev"),
                StateFilter('*'))
async def cmd_dev(message: Message, state: FSMContext):
    await message.answer(
        text='Вы в режиме разработчика. Выберите действие:',
        reply_markup=DevKeyboards().dev_inline()
    )


@router.callback_query(F.data == "hard_reset",
                       StateFilter('*'))
async def start_check(callback: CallbackQuery, state: FSMContext):
    state_before = await state.get_state()
    await state.clear()
    time.sleep(1)
    state_after = await state.get_state()
    await callback.message.answer(
        text=f'Состояние сброшено с {state_before} на {state_after}\nВы можете авторизоваться',
        reply_markup=DefaultKeyboards().get_authorization()
    )
    await callback.answer()

@router.callback_query(F.data == "check_state",
                       StateFilter('*'))
async def cmd_start(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await callback.message.answer(f"Вы находитесь в состоянии: {current_state}")
    await callback.answer()




