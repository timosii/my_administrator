import datetime as dt

def time_determiner():
    tz = dt.timezone(dt.timedelta(hours=3), name='Europe/Moscow')
    current_date = dt.datetime.now(tz=tz).strftime('%d.%m.%Y')
    return current_date


def format_timedelta(td):
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

    if days > 0:
        return f"{days} {end_day_definition(days)} {hours} {end_hour_definition(hours)} {minutes} {end_min_definition(minutes)}"
    if hours > 0:
        return f"{hours} {end_hour_definition(hours)} {minutes} {end_min_definition(minutes)}"
    else:
        return f"{minutes} {end_min_definition(minutes)}"
    

def get_index_by_violation_id(objects: list[object], violation_id: int):
    for index, obj in enumerate(objects):
        if obj.id == violation_id:
            return index
    return None


if __name__ == '__main__':
    print(time_determiner())
    td1 = dt.timedelta(minutes=50)
    td2 = dt.timedelta(hours=1, minutes=50)
    td3 = dt.timedelta(days=5, hours=1, minutes=50)
    td4 = dt.timedelta(days=0, hours=25, minutes=50)

    print(format_timedelta(td1))
    print(format_timedelta(td2))
    print(format_timedelta(td3))
    print(format_timedelta(td4))