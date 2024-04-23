from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.data import TIME_POINTS, ZONES


class MfcKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Начать проверку')
        self.kb.button(text='Назад')
        self.kb.adjust(2)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_check_time(self) -> ReplyKeyboardMarkup:
        for time in TIME_POINTS:
            self.kb.button(text=time)
        self.kb.button(text='Назад')
        self.kb.adjust(len(TIME_POINTS) + 1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_zone(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=zone) for zone in ZONES.keys()]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(len(ZONES) + 1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_violation(self, zone: str) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=violation) for violation in ZONES[zone]]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(len(ZONES[zone]) + 1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_photo_comm(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=s) for s in ['Загрузить фото', 'Написать комментарий']]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(3)
        return self.kb.as_markup(resize_keyboard=True)

    def back_level(self, zone: str) -> ReplyKeyboardMarkup:
        self.kb.button(f'Вернуться к блоку {zone}')
        self.kb.button('Вернуться к зонам нарушений')
        self.kb.adjust(2)
        return self.kb.as_markup(resize_keyboard=True)

    def add_photo_comm_kb(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
