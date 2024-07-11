import datetime as dt


def time_determiner() -> str:
    tz = dt.timezone(dt.timedelta(hours=3), name='Europe/Moscow')
    current_date = dt.datetime.now(tz=tz).strftime('%d.%m.%Y')
    return current_date


def form_greeting():
    tz = dt.timezone(dt.timedelta(hours=3), name='Europe/Moscow')
    current_hour = dt.datetime.now(tz=tz).hour
    if 0 <= current_hour < 6:
        greeting = 'Доброй ночи'
    if 6 <= current_hour < 12:
        greeting = 'Доброе утро'
    elif 12 <= current_hour < 18:
        greeting = 'Добрый день'
    else:
        greeting = 'Добрый вечер'
    return greeting
