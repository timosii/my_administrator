from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class DefaultKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def get_authorization(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Пройти авторизацию')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def feedback_kb(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Закончить отправку', callback_data='finish_feedback_')
            ]
        ])
        return self.kb
    


class DevKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def dev_inline(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Проверить состояние', callback_data='check_state'),
            ],
            [
                InlineKeyboardButton(text='Посмотреть данные состояния', callback_data='data_fsm'),
            ],
            [
                InlineKeyboardButton(text='Сбросить текущее состояние', callback_data='hard_reset'),
            ],
        ])
        return self.kb
    