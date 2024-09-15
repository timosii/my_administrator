from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from loguru import logger

from app.filters.default import VacationFilter
from app.handlers.messages import DefaultMessages

router = Router()
router.message.filter(VacationFilter())


@router.message()
async def vacation_message(
    message: Message,
    state: FSMContext,
):
    user = message.from_user
    logger.info(f'User {user.id} {user.username} passed authorization')
    await state.clear()
    await message.answer(
        text=DefaultMessages.vacation,
        reply_markup=ReplyKeyboardRemove()
    )
