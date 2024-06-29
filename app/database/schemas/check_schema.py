import datetime as dt

from pydantic import BaseModel

from app.utils.utils import format_timedelta, to_moscow_time


class CheckBase(BaseModel):
    fil_: str
    mfc_user_id: int
    is_task: bool


class CheckCreate(CheckBase):
    pass


class CheckTestCreate(CheckCreate):
    mfc_finish: dt.datetime


class CheckUpdate(BaseModel):
    # mo_user_id: Optional[int] = None
    mfc_finish: dt.datetime | None = None
    mo_start: dt.datetime | None = None
    mo_finish: dt.datetime | None = None


class CheckInDB(CheckBase):
    check_id: int
    mfc_start: dt.datetime
    mfc_finish: dt.datetime | None = None
    mo_start: dt.datetime | None = None
    mo_finish: dt.datetime | None = None

    class Config:
        from_attributes = True


class CheckOut(BaseModel):
    check_id: int
    fil_: str
    mfc_start: dt.datetime
    mfc_finish: dt.datetime
    violations_count: int

    def form_card_check_out(self) -> str:
        result = f"""
<b>Филиал:</b>
{self.fil_}
<b>Дата начала проверки:</b>
{to_moscow_time(self.mfc_start).strftime('%d.%m.%Y %H:%M')}
<b>Дата завершения проверки:</b>
{to_moscow_time(self.mfc_finish).strftime('%d.%m.%Y %H:%M')}
<b>Проверка заняла: {format_timedelta(self.mfc_finish - self.mfc_start)} </b>
<b>Количество активных нарушений:</b>
{self.violations_count}
        """
        return result

    class Config:
        from_attributes = True


class CheckOutUnfinished(BaseModel):
    fil_: str
    mfc_start: dt.datetime
    violations_count: int

    def form_card_unfinished_out(self):
        result = f"""
<b>Филиал:</b>
{self.fil_}
<b>Дата начала проверки:</b>
{to_moscow_time(self.mfc_start).strftime('%d.%m.%Y %H:%M')}
<b>Количество выявленных нарушений:</b>
{self.violations_count}
        """
        return result

    class Config:
        from_attributes = True
