from dataclasses import dataclass
from typing import Optional

from aiogram.types import InlineKeyboardMarkup

from app.database.schemas.violation_found_schema import ViolationFoundOut
from app.keyboards.mo_part import MoPerformerKeyboards


@dataclass
class Reply:
    photo_id: Optional[str]
    text_mes: str
    keyboard: InlineKeyboardMarkup


class FormCards:
    def __init__(self) -> None:
        pass

    def form_reply(self, violations_out: list[ViolationFoundOut], order: int):
        photo_id = violations_out[order].photo_id_mfc
        text_mes = violations_out[order].violation_card()
        prev_order = order - 1
        next_order = order + 1
        keyboard = MoPerformerKeyboards().get_violation_menu(
            prev_violation_id=violations_out[prev_order].violation_found_id,
            violation_id=violations_out[order].violation_found_id,
            next_violation_id=(
                violations_out[next_order].violation_found_id
                if order != (len(violations_out) - 1)
                else violations_out[0].violation_found_id
            ),
        )

        return Reply(photo_id=photo_id, text_mes=text_mes, keyboard=keyboard)

    def form_violation_pending_reply(self, violations_out: list[ViolationFoundOut], order: int):
        photo_id = violations_out[order].photo_id_mfc
        text_mes = violations_out[order].violation_card_pending()
        prev_order = order - 1
        next_order = order + 1
        keyboard = MoPerformerKeyboards().get_violation_pending_menu(
            prev_violation_id=violations_out[prev_order].violation_found_id,
            violation_id=violations_out[order].violation_found_id,
            next_violation_id=(
                violations_out[next_order].violation_found_id
                if order != (len(violations_out) - 1)
                else violations_out[0].violation_found_id
            ),
        )

        return Reply(photo_id=photo_id, text_mes=text_mes, keyboard=keyboard)
