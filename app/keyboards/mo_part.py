from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.database.db_helpers.form_menu import get_zone_violations, get_fils_by_mo


class MoPerformerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Посмотреть активные проверки')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    # async def choose_fil(self, mo: str) -> ReplyKeyboardMarkup:
    #     fils = await get_fils_by_mo(mo=mo)
    #     buttons = [KeyboardButton(text=fil) for fil in fils]
    #     self.kb.add(*buttons)
    #     self.kb.adjust(1)
    #     return self.kb.as_markup(resize_keyboard=True)
    
    def back_to_violations(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Продолжить проверку')
        self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def back_to_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Вернуться в меню')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def check_finished(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def check_or_tasks(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Активные уведомления')
        self.kb.button(text='Активные проверки')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    
    @staticmethod
    def get_under_violation_photo(violation_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Посмотреть фото", callback_data=f"photo_{violation_id}")
            ], 
            [
                InlineKeyboardButton(text='Нарушение исправлено', callback_data=f"correct_{violation_id}")
            ]
        ])
        return kb
    
    @staticmethod
    def get_violation_menu(
        violation_id: int,
        prev_violation_id: int,
        next_violation_id: int
        ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"prev_{prev_violation_id}"),
                InlineKeyboardButton(text='Исправить', callback_data=f"correct_{violation_id}"),
                InlineKeyboardButton(text="➡️", callback_data=f"next_{next_violation_id}")
            ], 
        ], row_width=3)
        return kb
    
    @staticmethod
    def add_photo(violation_id) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Написать комментарий", callback_data=f"comm_after_photo_{violation_id}")
            ]
        ])
        return kb
    
    @staticmethod
    def add_comm(violation_id) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Отправить фото", callback_data=f"photo_after_comm_{violation_id}")
            ]
        ])
        return kb
    
    @staticmethod
    def vio_correct_with_photo(violation_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Нарушение исправлено', callback_data=f"correct_{violation_id}")
            ]
        ])
        return kb
    
    @staticmethod
    def get_under_check(check_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Посмотреть нарушения", callback_data=f"violations_{check_id}"),
            ],
        ])
        return kb
    
    @staticmethod
    def save_violation_found(violation_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Сохранить", callback_data=f"save_{violation_id}"),
            ],
        ])
        return kb
    
    

class MoControlerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Посмотреть неисправленные нарушения')
        self.kb.button(text='Посмотреть все нарушения')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
