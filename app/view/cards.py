import datetime as dt
from dataclasses import dataclass
from typing import Optional
from app.utils.utils import format_timedelta
from app.database.schemas.check_schema import CheckOut, CheckOutUnfinished
from app.database.schemas.violation_found_schema import ViolationFoundOut
from app.keyboards.mo_part import MoPerformerKeyboards
from aiogram.types import InlineKeyboardMarkup


@dataclass
class Reply:
    photo_id: str
    text_mes: str
    keyboard: InlineKeyboardMarkup


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

    @staticmethod
    def check_card_unfinished(check: CheckOutUnfinished) -> str:
        result = f"""
<b>Филиал:</b>
{check.fil_}
<b>Дата начала проверки:</b>
{check.mfc_start.strftime('%d.%m.%Y %H:%M')}
<b>Количество выявленных нарушений:</b>
{check.violations_count}
        """
        return result

    def form_reply(self, violations_out: list[ViolationFoundOut], order: int):
        try:
            photo_id = violations_out[order].photo_id
        except TypeError:
            return None
                    
        text_mes = self.violation_card(violation=violations_out[order])
        keyboard = MoPerformerKeyboards().get_violation_menu(
            prev_violation_id=violations_out[order - 1].id,
            violation_id=violations_out[order].id,
            next_violation_id=(
                violations_out[order + 1].id
                if order != (len(violations_out) - 1)
                else violations_out[0].id
            ),
        )

        return Reply(photo_id=photo_id, text_mes=text_mes, keyboard=keyboard)
