from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database.services.users import UserService


class VacationFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user_id = message.from_user.id

        return await UserService().is_vacation(user_id=user_id)


async def not_back_filter(message: Message) -> bool:
    return message.text.lower() != 'назад'


async def not_menu_filter(message: Message) -> bool:
    menu = [
        '/start',
        '/feedback',
        '/changelog',
        '/dev',
        '/docs'
    ]
    res = message.text.lower() not in menu
    return res


async def not_buttons_filter(message: Message) -> bool:
    buttons = [
        'Пропустить',
        'Добавить пользователя',
        'Перенесенные нарушения',
        'Удалить пользователя',
        'Посмотреть пользователей',
        'Посмотреть отчеты',
        'Назад',
        'Проверить незавершенные проверки',
        'Добавить уведомление о нарушении',
        'Начать проверку',
        '⛔️ Закончить проверку',
        '⬅️ К выбору зоны',
        'Отменить',
        'Добавить пользователя',
        'Посмотреть отчет о работе сотрудников МФЦ',
        'Активные уведомления',
        'Активные проверки',
        'Вернуться в меню',
        'Написать комментарий',
        'Загрузить фото',
    ]
    res = message.text not in buttons
    return res


async def not_cancel_filter(message: Message) -> bool:
    return message.text.lower() != 'отменить'


async def not_constants(message: Message) -> bool:
    if not message.text:
        return False
    return (await not_cancel_filter(message=message)) & (await not_buttons_filter(message=message)) & (await not_menu_filter(message=message)) & (await not_back_filter(message=message))


async def is_digit(message: Message) -> bool:
    return message.text.isdigit()
