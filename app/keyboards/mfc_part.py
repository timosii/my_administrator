from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from app.data import TIME_POINTS, ZONES

def choose_check_time() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for time in TIME_POINTS:
        kb.button(text=time)
    kb.adjust(len(TIME_POINTS))
    return kb.as_markup(resize_keyboard=True)


def choose_zone() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for zone in ZONES.keys():
        kb.button(zone)
    kb.adjust(len(ZONES))
    return kb.as_markup(resize_keyboard=True)


def choose_violation(zone: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for violation in ZONES[zone]:
        kb.button(violation)
    kb.adjust(len(ZONES[zone]))
    return kb.as_markup(resize_keyboard=True)


def choose_photo_comm() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button('Загрузить фото')
    kb.button('Написать комментарий')
    return kb.as_markup(resize_keyboard=True)


def back_level(zone: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(f'Вернуться к блоку {zone}')
    kb.button('Вернуться к зонам нарушений')
    return kb.as_markup(resize_keyboard=True)

