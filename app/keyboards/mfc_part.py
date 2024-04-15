from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def choose_check_time() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="8:00")
    kb.button(text="12:00")
    kb.button(text="16:00")
    kb.button(text="20:00")
    kb.adjust(4)
    return kb.as_markup(resize_keyboard=True)