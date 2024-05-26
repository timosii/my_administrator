from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.database.db_helpers.form_menu import get_zone_violations, get_zones, get_fils_by_mo


class MoPerformerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Проверить нарушения')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    async def choose_fil(self, mo: str) -> ReplyKeyboardMarkup:
        fils = await get_fils_by_mo(mo=mo)
        buttons = [KeyboardButton(text=fil) for fil in fils]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def get_under_violation(self, violation_id: int) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Посмотреть комментарий", callback_data=f"comment_{violation_id}"),
            ],
            [
                InlineKeyboardButton(text="Посмотреть фото", callback_data=f"photo_{violation_id}")
            ]
        ])
        return self.kb    

class MoControlerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Посмотреть неисправленные нарушения')
        self.kb.button(text='Посмотреть все нарушения')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
