import datetime as dt

from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel


class Reply(BaseModel):
    photo: str
    caption: str
    reply_markup: InlineKeyboardMarkup


class MoCheckDefaultInfo(BaseModel):
    fil_: str
    mo: str
    mo_user_id: int


class MoCheckStarted(MoCheckDefaultInfo):
    check_id: int
    mo_start: dt.datetime  # не забыть преобразовывать в строку
