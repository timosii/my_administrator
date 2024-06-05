import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.database.db_helpers.form_menu import get_zone_violations, get_zones, get_fils_by_mo


class DefaultKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def get_authorization(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Пройти авторизацию')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)


class MfcKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Начать проверку')
        self.kb.button(text='Проверить незавершенные проверки')
        self.kb.button(text='Добавить уведомление о нарушении')
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

    def choose_zone(self) -> ReplyKeyboardMarkup:
        zones = get_zones()
        buttons = [KeyboardButton(text=zone) for zone in zones]
        self.kb.add(*buttons)
        self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_violation(self, zone: str) -> ReplyKeyboardMarkup:
        violations = await get_zone_violations(zone=zone)
        buttons = [KeyboardButton(text=violation) for violation in violations]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def choose_photo_comm(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=s) for s in ['Загрузить фото', 'Написать комментарий']]
        self.kb.add(*buttons)
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def just_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def photo_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить комментарий', callback_data='add_comm_'),
            ]
        ])
        return self.kb
    
    def take_task_to_work(self, violation_id: int, is_task: int) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Взять в работу', callback_data=f'take_{violation_id}_{is_task}'),
            ]
        ])
        return self.kb
    
    def get_description(self, violation_id: int) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Посмотреть описание нарушения', callback_data=f'description_{violation_id}'),
            ]
        ])
        return self.kb
    
    def unfinished_check(self, check_id) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Удалить проверку', callback_data=f'delete_unfinished_check_{check_id}'),
            ],
            [
                InlineKeyboardButton(text='Продолжить проверку', callback_data=f'finish_unfinished_check_{check_id}'),
            ],
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
            ]
        ])
        return self.kb


class MfcLeaderKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Добавить пользователя')
        self.kb.button(text='Посмотреть отчет о работе сотрудников МФЦ')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
