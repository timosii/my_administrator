from aiogram import F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message

from app.handlers.messages import DefaultMessages

router = Router()


@router.message(
    or_f(Command('start'), F.text.lower() == 'назад'),
    StateFilter(default_state)
)
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=DefaultMessages.start_message,
    )
