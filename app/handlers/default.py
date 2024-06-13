import time
from aiogram import Router, F, Bot
from aiogram.filters import Command, or_f
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from app.keyboards.default import DefaultKeyboards
# from app.keyboards.mfc_inline import MfcKeyboards
from app.handlers.messages import DefaultMessages
from app.handlers.states import MfcStates, Feedback
from app.filters.mfc_filters import MfcFilter
from app.filters.default import not_back_filter, not_cancel_filter, not_menu_filter
from loguru import logger
from app.config import settings
from app.misc.changelog import CHANGELOG

router = Router() 

@router.message(
    or_f(Command("start"),F.text.lower() == "назад"),
    StateFilter(default_state)
)
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=DefaultMessages.start_message,
        reply_markup=DefaultKeyboards().get_authorization()
    )

@router.message(Command("feedback"))
async def get_feedback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(f'STATE IS: {current_state}')
    await message.answer(
        text=DefaultMessages.feedback,
        reply_markup=DefaultKeyboards().feedback_kb()
    )
    await state.update_data(
        state_current_for_fb=current_state
    )
    await state.set_state(Feedback.feedback)

@router.message(F.text,
                not_menu_filter,
                not_back_filter,
                not_cancel_filter,
                StateFilter(Feedback.feedback))
async def take_feedback(message: Message, state: FSMContext, bot: Bot):
    res = message.text
    await bot.send_message(
        chat_id=settings.DEV_ID,
        text=f'{message.from_user.id} {message.from_user.username} хочет сказать:\n{res}'
    )
    await message.answer(
        text=DefaultMessages.feedback_answer,
        reply_markup=DefaultKeyboards().feedback_kb()
    )

@router.message(F.photo,
                StateFilter(Feedback.feedback))
async def take_feedback(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    caption_ = message.caption
    await bot.send_photo(
        chat_id=settings.DEV_ID,
        photo=photo_id,
        caption=f'{message.from_user.id} {message.from_user.username} прислал фото:\n{caption_ if caption_ else ""}'
    )

    await message.answer(
        text=DefaultMessages.feedback_answer,
        reply_markup=DefaultKeyboards().feedback_kb()
    )

@router.callback_query(
    F.data == 'finish_feedback_',
    StateFilter(Feedback.feedback)
)
async def cancel_feedback(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        text=DefaultMessages.feedback_answer_finish,
    )
    data = await state.get_data()
    state_back = data['state_current_for_fb']
    if state_back != Feedback.feedback:
        await state.set_state(state_back)
    else:
        await state.clear()        
    await callback.answer()


@router.message(~F.text & ~F.photo,
                StateFilter(Feedback.feedback))
async def take_feedback(message: Message,
                        state: FSMContext):
    await message.answer(
        text=DefaultMessages.not_good_time,
    )
