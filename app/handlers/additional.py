from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.filters.admin import AdminFilter
from app.filters.default import not_constants
from app.filters.mfc_filters import MfcFilter, MfcLeaderFilter
from app.filters.mo_filters import MoControlerFilter, MoPerformerFilter
from app.handlers.messages import DefaultMessages
from app.handlers.states import Feedback
from app.keyboards.default import DefaultKeyboards

router = Router()
router.message.filter(
    or_f(
        MoPerformerFilter(),
        MoControlerFilter(),
        MfcFilter(),
        MfcLeaderFilter(),
        AdminFilter()
    )
)


@router.message(Command('feedback'))
async def get_feedback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(
        text=DefaultMessages.feedback,
        reply_markup=DefaultKeyboards().feedback_kb()
    )
    await state.update_data(
        state_current_for_fb=current_state
    )
    await state.set_state(Feedback.feedback)


@router.message(Command('changelog'))
async def changelog(message: Message, state: FSMContext):
    await message.answer(
        text=DefaultMessages.send_changelog,
    )


@router.message(Command('docs'))
async def docs_command(message: Message):
    await message.answer(
        text='Перейдите по ссылке, чтобы открыть документацию',
        reply_markup=DefaultKeyboards.get_docs()
    )


@router.message(F.text,
                not_constants,
                StateFilter(Feedback.feedback))
async def take_feedback_text(message: Message, bot: Bot):
    res = message.text
    await bot.send_message(
        chat_id=settings.DEV_ID,
        text=f'#feedback\n{message.from_user.id} {message.from_user.username} хочет сказать:\n{res}'
    )
    await message.answer(
        text=DefaultMessages.feedback_answer,
        reply_markup=DefaultKeyboards().feedback_kb()
    )


@router.message(F.photo,
                StateFilter(Feedback.feedback))
async def take_feedback_photo(message: Message, bot: Bot):
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
async def take_feedback_wrong(message: Message):
    await message.answer(
        text=DefaultMessages.not_good_time,
    )
