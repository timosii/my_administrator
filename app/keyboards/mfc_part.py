from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


from app.database.db_helpers.form_menu import (
    get_all_zones,
    get_fils_by_mo,
    get_zone_violations,
)
from app.view.menu_beautify import ICONS_MAPPING


class DefaultKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()


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

    async def choose_mo(self, mos: list[str]) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=mo) for mo in mos]
        self.kb.add(*buttons)
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_zone(self) -> ReplyKeyboardMarkup:
        zones = await get_all_zones()
        buttons = [KeyboardButton(text=f'{ICONS_MAPPING[zone]} {zone}') for zone in zones]
        self.kb.add(*buttons)
        self.kb.button(text='⛔️ Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_violation(self, zone: str, completed_violations: list) -> ReplyKeyboardMarkup:
        violations = await get_zone_violations(zone=zone)
        buttons = [KeyboardButton(
            text=f'✅ {violation}' if violation in completed_violations else f'{violation}') for violation in violations]
        self.kb.button(text='⬅️ К выбору зоны')
        self.kb.add(*buttons)
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def add_content(self) -> ReplyKeyboardMarkup:
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

    @staticmethod
    def get_violation_pending_menu(
        violation_id: int,
        prev_violation_id: int,
        next_violation_id: int
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='⬅️', callback_data=f'prev_{prev_violation_id}'),
                InlineKeyboardButton(text='➡️', callback_data=f'next_{next_violation_id}')
            ],
            [
                InlineKeyboardButton(text='Добавить новое нарушение', callback_data='new_'),
            ],
            [
                InlineKeyboardButton(text='Вернуться к нарушениям', callback_data=f'back_{violation_id}'),
            ]
        ])
        return kb


class MfcLeaderKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Добавить пользователя')
        self.kb.button(text='Посмотреть отчет о работе сотрудников МФЦ')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def get_report(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Выбрать период')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def get_end_of_period(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Выбрать период')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
        
