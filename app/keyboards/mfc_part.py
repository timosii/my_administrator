from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.database.db_helpers.form_menu import (
    get_all_zones,
    get_violation_problems,
    get_zone_violations,
)
from app.view.menu_beautify import ICONS_MAPPING

SPECS = [
    'Акушер-гинеколог (детский)',
    'Аллерголог',
    'Гастроэнтеролог',
    'Инфекционист',
    'Кардиолог',
    'Колопроктолог',
    'Невролог',
    'Нефролог (детский)',
    'Оториноларинголог',
    'Офтальмолог',
    'Пульмонолог',
    'Уролог',
    'Участковый врач',
    'Хирург',
    'Эндокринолог',
    'ЭХО-КГ',
    'ЭКГ',
    'Гастроскопия',
    'Холтер',
    'ФВД',
    'Флюорография',
    'УЗИ',
    'УЗДГ-УЗДС-БЦА',
    'СМАД',
    'Рентген',
    'Маммография',
    'КТ',
    'МРТ',
    'Взятие крови',
]


class MfcKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    async def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Начать проверку')
        self.kb.button(text='Проверить незавершенные проверки')
        self.kb.button(text='Добавить уведомление о нарушении')
        self.kb.button(text='Доступность у инфомата')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_zone(self) -> ReplyKeyboardMarkup:
        zones = await get_all_zones()
        buttons = [
            KeyboardButton(text=f'{ICONS_MAPPING[zone]} {zone}') for zone in zones
        ]
        self.kb.add(*buttons)
        self.kb.button(text='⛔️ Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_violation(
        self, zone: str, completed_violations: list
    ) -> ReplyKeyboardMarkup:
        violations = await get_zone_violations(zone=zone)
        buttons = [
            KeyboardButton(
                text=(
                    f'✅ {violation}'
                    if violation in completed_violations
                    else f'{violation}'
                )
            )
            for violation in violations
        ]
        self.kb.button(text='⬅️ К выбору зоны')
        self.kb.add(*buttons)
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def choose_problem(
        self, violation_name: str, zone: str, completed_problems: list
    ) -> ReplyKeyboardMarkup:
        problems = await get_violation_problems(violation_name=violation_name, zone=zone)
        buttons = [
            KeyboardButton(
                text=(
                    f'✅ {problem}'
                    if problem in completed_problems
                    else f'{problem}'
                )
            )
            for problem in problems
        ]
        self.kb.button(text='⬅️ К выбору нарушения')
        self.kb.add(*buttons)
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def add_content(self) -> ReplyKeyboardMarkup:
        buttons = [
            KeyboardButton(text=s) for s in ['Загрузить фото', 'Написать комментарий']
        ]
        self.kb.add(*buttons)
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def just_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def finish_photo_addition(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Закончить добавление фото')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def avail_cancel(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    async def avail_cancel_yes(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Да')
        self.kb.button(text='Отменить')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    @staticmethod
    async def get_specs() -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=spec, callback_data=f'spec_{spec}')
                    for spec in SPECS[i: i + 2]
                ]
                for i in range(0, len(SPECS), 2)
            ]
        )
        return kb

    async def photo_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Добавить комментарий', callback_data='add_comm_'
                    ),
                ]
            ]
        )
        return self.kb

    async def all_photo_remove(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Убрать', callback_data='remove_allphoto'
                    ),
                ]
            ]
        )
        return self.kb

    async def take_task_to_work(
        self, violation_id: str, is_task: int
    ) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Получить все фото для этого нарушения',
                                         callback_data=f'allphoto_{violation_id}'),
                ],
                [
                    InlineKeyboardButton(
                        text='Исправить сразу',
                        callback_data=f'take_{violation_id}_{is_task}',
                    ),
                ],

            ]
        )
        return self.kb

    # async def get_description(self, violation_id: int) -> InlineKeyboardMarkup:
    #     self.kb = InlineKeyboardMarkup(
    #         inline_keyboard=[
    #             [
    #                 InlineKeyboardButton(
    #                     text='Посмотреть описание нарушения',
    #                     callback_data=f'description_{violation_id}',
    #                 ),
    #             ]
    #         ]
    #     )
    #     return self.kb

    async def unfinished_check(self, check_id) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Удалить проверку',
                        callback_data=f'delete_unfinished_check_{check_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='Продолжить проверку',
                        callback_data=f'finish_unfinished_check_{check_id}',
                    ),
                ],
            ]
        )
        return self.kb

    async def comm_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Добавить фото', callback_data='add_photo_'
                    ),
                ]
            ]
        )
        return self.kb

    async def save_or_cancel(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Сохранить', callback_data='save_and_go'),
                ],
                [
                    InlineKeyboardButton(
                        text='Добавить фотографии', callback_data='additional_photo'
                    )
                ],
            ]
        )
        return self.kb

    @staticmethod
    async def get_violation_pending_menu(
        violation_id: str, prev_violation_id: str, next_violation_id: str
    ) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                # [
                #     InlineKeyboardButton(
                #         text="⬅️ 📷", callback_data=f"pphoto_{violation_id}"
                #     ),
                #     InlineKeyboardButton(
                #         text="📷 ➡️", callback_data=f"nphoto_{violation_id}"
                #     ),
                # ],
                [
                    InlineKeyboardButton(text='Получить все фото для этого нарушения',
                                         callback_data=f'allphoto_{violation_id}'),
                ],
                [
                    InlineKeyboardButton(
                        text='⏪️', callback_data=f'prev_{prev_violation_id}'
                    ),
                    InlineKeyboardButton(
                        text='⏩️', callback_data=f'next_{next_violation_id}'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='Добавить новое нарушение', callback_data='new_'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='Вернуться к нарушениям',
                        callback_data=f'back_{violation_id}',
                    ),
                ],
            ]
        )
        return kb


class MfcLeaderKeyboards:
    def __init__(self) -> None:
        self.kb = ReplyKeyboardBuilder()

    def main_menu(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Отпуск сотрудника')
        self.kb.button(text='Посмотреть отчет о работе сотрудников МФЦ')
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def get_period(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Выбрать период')
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
