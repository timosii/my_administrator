import datetime as dt

def time_determiner():
    tz = dt.timezone(dt.timedelta(hours=3), name='Europe/Moscow')
    current_date = dt.datetime.now(tz=tz).strftime('%d.%m.%Y')
    return current_date

if __name__ == '__main__':
    print(time_determiner())