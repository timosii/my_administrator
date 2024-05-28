import datetime as dt
from typing import Optional
from app.utils.utils import format_timedelta


class FormCards:
    def __init__(self) -> None:
        pass

    @staticmethod
    def violation_card(
        violation_zone: str,
        violation_name: str,
        violation_detected: dt.datetime,
        violation_duration: dt.timedelta,
        violation_comm: Optional[str] = None,
    ):
        result = f"""
<b>Зона:</b>
{violation_zone}
<b>Нарушение:</b>
{violation_name}
<b>Время выявления нарушения:</b>
{violation_detected.strftime('%d.%m.%Y %H:%M')}

Комментарий: {violation_comm if violation_comm else 'отсутствует'}
Время на исправление: {format_timedelta(violation_duration)}
        """
        return result

    @staticmethod
    def check_card(
        check_fil_: str,
        check_start: dt.datetime,
        check_finish: dt.datetime,
        violations_count: int,
    ) -> str:
        result = f"""
<b>Филиал:</b>
{check_fil_}
<b>Дата начала проверки:</b>
{check_start.strftime('%d.%m.%Y %H:%M')}
<b>Дата завершения проверки:</b>
{check_finish.strftime('%d.%m.%Y %H:%M')}
<b>Проверка заняла: {format_timedelta(check_finish - check_start)} </b>
<b>Количество нарушений:</b>
{violations_count}
        """
        return result
    