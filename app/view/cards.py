import datetime as dt
from typing import Optional


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
Время на исправление: {str(violation_duration)}
        """
        return result

    @staticmethod
    def check_card(
        check_fil_: str,
        check_date: dt.datetime,
        violations_count: int,
    ) -> str:
        result = f"""
<b>Дата проверки:</b>
{check_date.strftime('%d-%m-%Y')}
<b>Филиал проверки:</b>
{check_fil_}
<b>Количество нарушений:</b>
{violations_count}
        """
        return result
