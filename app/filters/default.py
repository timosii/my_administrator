from aiogram.types import Message


async def not_back_filter(message: Message) -> bool:
    return message.text.lower() != 'назад'


async def not_menu_filter(message: Message) -> bool:
    menu = [
        '/start',
        '/feedback',
        '/changelog',
        '/dev'
    ]
    res = message.text.lower() not in menu
    return res


async def not_buttons_filter(message: Message) -> bool:
    buttons = [
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
