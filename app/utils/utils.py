import datetime as dt
import pytz
from loguru import logger
# from app.database.services.users import UserService
from dataclasses import dataclass
from typing import Optional


@dataclass
class Name:
    last_name: str
    first_name: str
    patronymic: Optional[str]

    def get_greeting_name(self):
        if self.patronymic:
            return f'{self.first_name} {self.patronymic}'
        else:
            return f'{self.first_name}'


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


def to_moscow_time(date: dt.datetime) -> dt.datetime:
    utc_zone = pytz.utc
    moscow_zone = pytz.timezone('Europe/Moscow')

    date_utc = date.replace(tzinfo=utc_zone)
    date_moscow = date_utc.astimezone(moscow_zone)
    date_moscow_naive = date_moscow.replace(tzinfo=None)
    
    return date_moscow_naive


def ending_define(num: int) -> str:
    if num == 1:
        return 'у'
    else:
        return 'ам'
    
def define_word(num: int) -> str:
    if num == 1:
        return 'ему'
    else:
        return 'им'    


def format_timedelta(td: dt.timedelta):
    total_minutes = int(td.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    days, hours = divmod(hours, 24)
    
    def end_day_definition(days: int):
        if days in (2, 3, 4, 22, 23, 24):
            return 'дня' 
        elif days in range(5,21):
            return 'дней'
        else:
            return 'день'     
    
    def end_hour_definition(hours: int):
        if hours in (2, 3, 4, 22, 23):
            return 'часа'
        elif hours in range(5, 21) or hours == 0:
            return 'часов'
        else:
            return 'час'
        
    def end_min_definition(minutes: int):
        if 11 <= minutes <= 19:
            return 'минут'

        last_digit = minutes % 10
        if last_digit == 1:
            return 'минута'
        elif last_digit in (2, 3, 4):
            return 'минуты'
        else:
            return 'минут'
    
    days_out = f"{days} {end_day_definition(days)}" if days > 0 else ''
    hours_out = f"{hours} {end_hour_definition(hours)}" if hours > 0 else ''
    minutes_out = f"{minutes} {end_min_definition(minutes)}" if minutes > 0 else ''

    if days > 0:
        result = f"{days_out} {hours_out} {minutes_out}"
    elif hours > 0:
        result = f"{hours_out} {minutes_out}"
    else:
        result = f"{minutes_out}" if minutes_out else '1 минуту'
        
    return result

def get_index_by_violation_id(objects: list[object], violation_found_id: int) -> int | None:
    for index, obj in enumerate(objects):
        if obj.violation_found_id == violation_found_id:
            return index
    return 0


if __name__ == '__main__':
    pass
    # td1 = dt.timedelta(days=0, hours=0, minutes=5)
    # td2 = dt.timedelta(days=5, hours=1, minutes=50)
    # td3 = dt.timedelta(days=0, hours=0, minutes=30)
    # td4 = dt.timedelta(days=1, hours=0, minutes=0)

    # print(format_timedelta(td1))
    # print(format_timedelta(td2))
    # print(format_timedelta(td3))
    # print(format_timedelta(td4))
    # time = dt.datetime.now()
    # print(time_moscow(time))