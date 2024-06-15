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
from app.filters.default import not_constants
from loguru import logger
from app.config import settings
from app.view.changelog import CHANGELOG

router = Router() 

@router.message(
    or_f(Command("start"),F.text.lower() == "назад"),
    StateFilter(default_state)
)
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(
        text=DefaultMessages.start_message,
    )
