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

from app.database.repositories.violations_found import ViolationFoundRepo

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
async def hard_reset(callback: CallbackQuery, state: FSMContext):
    state_before = await state.get_state()
    await state.clear()
    state_after = await state.get_state()
    await callback.message.answer(
        text=f'Состояние сброшено с {state_before} на {state_after}\nВы можете авторизоваться',
        reply_markup=DefaultKeyboards().get_authorization()
    )
    await callback.answer()

@router.callback_query(F.data == "check_state",
                       StateFilter('*'))
async def сheck_state(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await callback.message.answer(f"Вы находитесь в состоянии: {current_state}")
    await callback.answer()

@router.callback_query(F.data == "data_fsm",
                       StateFilter('*'))
async def data_fsm(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    await callback.message.answer(f'{current_data}')
    await callback.answer()
