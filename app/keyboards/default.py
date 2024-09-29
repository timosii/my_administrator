from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.config import settings
from app.database.db_helpers.form_menu import get_fils_by_mo

DOCS_URL = settings.DOCS_URL
DOCS_MFC = settings.DOCS_MFC
DOCS_MO = settings.DOCS_MO


DOCS_MAPPING = {
    'mfc': DOCS_MFC,
    'mo': DOCS_MO,
}


class DefaultKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def feedback_kb(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Закончить отправку', callback_data='finish_feedback_')
            ]
        ])
        return self.kb

    @staticmethod
    def get_docs(role: str) -> InlineKeyboardMarkup:

        url = DOCS_MAPPING[role]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Нажмите сюда',
                    web_app=WebAppInfo(url=url)
                )
            ],
        ])
        return kb

    def choose_mo(self, mos: list[str]) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=mo) for mo in mos]
        self.kb.add(*buttons)
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


class ToVacationKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def finish_process(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Закончить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_employee(self,
                        user_id: int) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Поменять статус', callback_data=f'choose_employee_{user_id}'),
                ],
            ]
        )
        return self.kb
