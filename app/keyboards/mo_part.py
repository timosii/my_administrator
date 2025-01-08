from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class MoPerformerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    async def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Посмотреть активные проверки')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def just_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def back_to_violations(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Продолжить проверку')
        self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def back_to_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Вернуться в меню')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def check_finished(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def check_or_tasks(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Активные уведомления')
        self.kb.button(text='Активные проверки')
        self.kb.button(text='Перенесенные нарушения')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    @staticmethod
    async def get_violation_menu(
        violation_id: str,
        prev_violation_id: str,
        next_violation_id: str
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Получить все фото для этого нарушения',
                                     callback_data=f'allphoto_{violation_id}'),
            ],
            [
                InlineKeyboardButton(text='⏪️', callback_data=f'prev_{prev_violation_id}'),
                InlineKeyboardButton(text='Исправить', callback_data=f'correct_{violation_id}'),
                InlineKeyboardButton(text='⏩️', callback_data=f'next_{next_violation_id}')
            ],
            [
                InlineKeyboardButton(text='Перенести исправление', callback_data=f'pending_{violation_id}'),
            ]
        ], row_width=3)
        return kb

    @staticmethod
    async def get_violation_pending_menu(
        violation_id: str,
        prev_violation_id: str,
        next_violation_id: str
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            # [
            #     InlineKeyboardButton(text='⬅️ 📷', callback_data=f'pphoto_{violation_id}'),
            #     InlineKeyboardButton(text='📷 ➡️', callback_data=f'nphoto_{violation_id}')
            # ],
            [
                InlineKeyboardButton(text='Получить все фото для этого нарушения',
                                     callback_data=f'allphoto_{violation_id}'),
            ],
            [
                InlineKeyboardButton(text='⏪️', callback_data=f'prev_{prev_violation_id}'),
                InlineKeyboardButton(text='Исправить', callback_data=f'correct_{violation_id}'),
                InlineKeyboardButton(text='⏩️', callback_data=f'next_{next_violation_id}')
            ],
        ], row_width=3)
        return kb

    @staticmethod
    async def get_under_check(check_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Посмотреть нарушения', callback_data=f'violations_{check_id}'),
            ],
        ])
        return kb

    @staticmethod
    async def get_under_check_zero_violations(check_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Закончить проверку', callback_data=f'violationszero_{check_id}'),
            ],
        ])
        return kb

    @staticmethod
    async def save_violation_found(violation_found_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Сохранить', callback_data=f'save_{violation_found_id}'),
            ],
            [
                InlineKeyboardButton(text='Отменить', callback_data=f'cancelsave_{violation_found_id}'),
            ],
        ])
        return kb

    @staticmethod
    async def cancel_correct_mode(violation_found_id: str) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Отменить', callback_data=f'cancel_{violation_found_id}'),
            ],
        ])
        return kb


class MoControlerKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отпуск сотрудника')
        self.kb.button(text='Посмотреть нарушения филиала')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def get_report(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Получить отчет')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

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
