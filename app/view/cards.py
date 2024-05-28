import datetime as dt
from typing import Optional
from app.utils.utils import format_timedelta
from app.database.schemas.check_schema import CheckOut
from app.database.schemas.violation_found_schema import ViolationFoundOut


class FormCards:
    def __init__(self) -> None:
        pass

    @staticmethod
    def violation_card(violation: ViolationFoundOut) -> str:
        result = f"""
<b>Зона:</b>
{violation.zone}
<b>Нарушение:</b>
{violation.violation_name}
<b>Время выявления нарушения:</b>
{violation.violation_detected.strftime('%d.%m.%Y %H:%M')}

Комментарий: {violation.comm if violation.comm else 'отсутствует'}
Время на исправление: {format_timedelta(violation.time_to_correct)}
        """
        return result

    @staticmethod
    def check_card(check: CheckOut) -> str:
        result = f"""
<b>Филиал:</b>
{check.fil_}
<b>Дата начала проверки:</b>
{check.mfc_start.strftime('%d.%m.%Y %H:%M')}
<b>Дата завершения проверки:</b>
{check.mfc_finish.strftime('%d.%m.%Y %H:%M')}
<b>Проверка заняла: {format_timedelta(check.mfc_finish - check.mfc_start)} </b>
<b>Количество нарушений:</b>
{check.violations_count}
        """
        return result
    