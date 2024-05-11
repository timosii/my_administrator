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

    def back_level(self, zone: str) -> ReplyKeyboardMarkup:
        self.kb.button(f'Вернуться к блоку {zone}')
        self.kb.button('Вернуться к зонам нарушений')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)

    def just_back(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Назад')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def just_back_finish(self) -> ReplyKeyboardMarkup:
        self.kb.button(text='Продолжить проверку')
        # self.kb.button(text='Закончить проверку')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def photo_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить комментарий', callback_data='add_comm_'),
                # InlineKeyboardButton(text='Вернуться к зонам нарушений', callback_data='continue_check_zones'),
                # InlineKeyboardButton(text=f'Вернуться к блоку {zone}', callback_data='continue_check_violations'),
                # InlineKeyboardButton(text='Продолжить проверку', callback_data='continue_check_')
            ]
        ])
        return self.kb
    
    def comm_added(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить фото', callback_data='add_photo_'),
                # InlineKeyboardButton(text='Вернуться к зонам нарушений', callback_data='continue_check_zones'),
                # InlineKeyboardButton(text=f'Вернуться к блоку проблематики {zone}', callback_data='continue_check_violations'),
            ]
        ])
        return self.kb
    
    def continue_finish_check(self, zone: str) -> ReplyKeyboardMarkup:
        self.kb.button(text='Вернуться к выбору зоны')
        self.kb.button(text=f'Вернуться к нарушениям зоны {zone}')
        self.kb.adjust(1)
        return self.kb.as_markup(resize_keyboard=True)
    
    def save_or_cancel(self) -> InlineKeyboardMarkup:
        self.kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Сохранить', callback_data='save_and_go'),
                # InlineKeyboardButton(text=f'Вернуться к блоку проблематики {zone}', callback_data='continue_check_violations'),
            ],
            [
                InlineKeyboardButton(text='Отменить', callback_data='cancel'),
            ]

        ])
        return self.kb
    
    
    # def continue_finish_check(self, zone) -> InlineKeyboardMarkup:
    #     self.kb = InlineKeyboardMarkup(inline_keyboard=[
    #         [
    #             InlineKeyboardButton(text='Вернуться к зонам нарушений', callback_data='continue_check_zones')
    #         ],
    #         [
    #             InlineKeyboardButton(text=f'Вернуться к блоку проблематики {zone}', callback_data='continue_check_violations')
    #         ]
    #     ])
    #     return self.kb   
