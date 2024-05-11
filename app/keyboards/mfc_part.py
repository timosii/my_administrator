from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.data import TIME_POINTS, ZONES


class MfcKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Начать проверку')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_check_time(self) -> ReplyKeyboardMarkup:
        for time in TIME_POINTS:
            self.kb.button(text=time)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_zone(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=zone) for zone in ZONES.keys()]
        self.kb.add(*buttons)
        self.kb.button(text='Закончить проверку')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_violation(self, zone: str) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=violation) for violation in ZONES[zone]]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_photo_comm(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=s) for s in ['Загрузить фото', 'Написать комментарий']]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def photo_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить комментарий', callback_data='add_comm_'),
            ]
        ])
        return self.kb
    
    def comm_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить фото', callback_data='add_photo_'),
            ]
        ])
        return self.kb
    
    def save_or_cancel(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Сохранить', callback_data='save_and_go'),
            ],
            [
                InlineKeyboardButton(text='Отменить', callback_data='cancel'),
            ]

        ])
        return self.kb
