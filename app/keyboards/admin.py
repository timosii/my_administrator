from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class AdminKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Добавить пользователей')
        self.kb.button(text='Удалить пользователя')
        self.kb.button(text='Посмотреть пользователей')
        self.kb.button(text='Посмотреть отчеты')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)


class SelfRegistration:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    # def get_reg(self) -> ReplyKeyboardMarkup:
    #     self.kb.button(text='Зарегистрироваться')
    #     self.kb.adjust(1)
    #     return self.kb.as_markup(resize_keyboard=True)

    def yes_no(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Да')
        self.kb.button(text='Нет')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def are_you_sure(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Да')
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def get_active(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Вернуться в актив')
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def save_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Сохранить')
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def cancel_miss(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Пропустить')
        self.kb.button(text='Начать сначала')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def cancel_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def just_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def from_start(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Начать сначала')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def get_nonactive(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Удалить аккаунт')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
