from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.default import DevKeyboards

router = Router()


@router.message(Command('dev'),
                StateFilter('*'))
async def cmd_dev(message: Message, state: FSMContext):
    await message.answer(
        text='Вы в режиме разработчика. Выберите действие:',
        reply_markup=DevKeyboards().dev_inline()
    )


@router.callback_query(F.data == 'hard_reset',
                       StateFilter('*'))
async def hard_reset(callback: CallbackQuery, state: FSMContext):
    state_before = await state.get_state()
    await state.clear()
    state_after = await state.get_state()
    await callback.message.answer(
        text=f'Состояние сброшено с {state_before} на {state_after}\nВы можете начать заново',
    )
    await callback.answer()


@router.callback_query(F.data == 'check_state',
                       StateFilter('*'))
async def сheck_state(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    await callback.message.answer(f'Вы находитесь в состоянии: {current_state}')
    await callback.answer()


@router.callback_query(F.data == 'data_fsm',
                       StateFilter('*'))
async def data_fsm(callback: CallbackQuery, state: FSMContext):
    current_data = await state.get_data()
    await callback.message.answer(f'{current_data}')
    await callback.answer()
